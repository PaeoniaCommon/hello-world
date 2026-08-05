"""
Per-view parameter memory for a single MCP tool: `mrx-call-view(view_name, mrx_params)`.

Context discipline:
  READ   nothing goes in the system prompt. Notes for a view are loaded only when
         that view is actually called, and injected once per run per view.
  WRITE  after the run, only views touched in this run are considered, and the
         reflector LLM only runs for a view that errored or used an unseen param.
         It returns a *delta*, not a rewritten file.

Storage is a LangGraph BaseStore keyed by view_name, so nothing is loaded that
isn't asked for. InMemoryStore here; swap for PostgresStore unchanged.

Record shape, one per view:
    {"params": {"<param>": "<short note>"}, "required": ["<param>", ...]}
"""

from __future__ import annotations

import asyncio
import json
from collections import defaultdict
from typing import Any, Callable

from langchain.agents import create_agent
from langchain.agents.middleware import AgentMiddleware, ToolCallLimitMiddleware
from langchain.chat_models import init_chat_model
from langchain.messages import AIMessage, ToolMessage
from langchain.tools.tool_node import ToolCallRequest
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.memory import InMemoryStore

TOOL_NAME = "mrx-call-view"
NAMESPACE = ("mrx", "view_notes")


REFLECT_PROMPT = """You maintain parameter notes for one view of an internal data API.

View: {view}

Current notes (JSON):
{current}

Calls to this view in the run that just finished:
{calls}

Return ONLY a JSON object with this shape — a DELTA, not a full rewrite:
{{"params": {{"<param_name>": "<note, max {max_chars} chars>"}},
  "required": ["<param that must always be supplied>"],
  "remove": ["<param name whose note is now wrong>"]}}

Rules:
- Only include a param if this run taught you something not already in the notes:
  accepted value format, a value that errored, a default worth overriding, a param
  that must accompany another, a filter that keeps the result set usable.
- "required" is only for params whose absence caused a failure or an unusable result.
  Omit the key entirely if you learned nothing about requiredness.
- Nothing about the specific question asked or the data returned. Notes must be
  reusable for any future call to this view.
- Empty object {{}} if the run taught you nothing.
"""


class MrxViewMemory(AgentMiddleware):
    def __init__(
        self,
        model: str = "anthropic:claude-haiku-4-5-20251001",
        max_params: int = 25,
        max_note_chars: int = 160,
    ) -> None:
        super().__init__()
        self.reflector = init_chat_model(model)
        self.max_params = max_params
        self.max_note_chars = max_note_chars

    # ------------------------------------------------------------------ store

    @staticmethod
    async def _load(store, view: str) -> dict:
        if store is None or not view:
            return {}
        item = await store.aget(NAMESPACE, view)
        return item.value if item else {}

    @staticmethod
    async def _save(store, view: str, rec: dict) -> None:
        if store is not None:
            await store.aput(NAMESPACE, view, rec)

    # ----------------------------------------------------------------- render

    @staticmethod
    def _marker(view: str) -> str:
        return f"[learned-params:{view}]"

    def _render(self, rec: dict) -> str:
        lines = [f"  {k}: {v}" for k, v in rec.get("params", {}).items()]
        if req := rec.get("required"):
            lines.insert(0, f"  (always supply: {', '.join(req)})")
        return "Learned notes for this view:\n" + "\n".join(lines)

    def _already_shown(self, state: dict, view: str) -> bool:
        marker = self._marker(view)
        return any(
            isinstance(m, ToolMessage) and isinstance(m.content, str) and marker in m.content
            for m in state.get("messages", [])
        )

    # ------------------------------------------------------------- read path

    async def awrap_tool_call(
        self,
        request: ToolCallRequest,
        handler: Callable[[ToolCallRequest], Any],
    ) -> Any:
        if request.tool_call["name"] != TOOL_NAME:
            return await handler(request)

        args = request.tool_call.get("args") or {}
        view = args.get("view_name", "")
        params = args.get("mrx_params") or {}
        rec = await self._load(request.runtime.store, view)

        # Deterministic pre-flight — no LLM, no backend round trip.
        missing = [p for p in rec.get("required", []) if p not in params]
        if missing:
            return ToolMessage(
                content=(
                    f"{self._marker(view)} Not executed: required params missing "
                    f"({', '.join(missing)}). Retry with them set.\n{self._render(rec)}"
                ),
                tool_call_id=request.tool_call["id"],
                name=TOOL_NAME,
                status="error",
            )

        result = await handler(request)

        # Attach notes once per view per run, so a repeat call is already informed.
        if (
            rec.get("params")
            and isinstance(result, ToolMessage)
            and isinstance(result.content, str)
            and not self._already_shown(request.state, view)
        ):
            result.content = f"{self._marker(view)}\n{self._render(rec)}\n---\n{result.content}"
        return result

    # ------------------------------------------------------------ write path

    @staticmethod
    def _mrx_calls(messages: list) -> dict[str, list[dict]]:
        """Group this run's mrx-call-view calls by view_name."""
        pending: dict[str, dict] = {}
        by_view: dict[str, list[dict]] = defaultdict(list)
        for msg in messages:
            if isinstance(msg, AIMessage):
                for tc in msg.tool_calls or []:
                    if tc["name"] == TOOL_NAME:
                        pending[tc["id"]] = tc
            elif isinstance(msg, ToolMessage) and msg.tool_call_id in pending:
                tc = pending.pop(msg.tool_call_id)
                args = tc.get("args") or {}
                by_view[args.get("view_name", "")].append(
                    {
                        "params": args.get("mrx_params") or {},
                        "ok": msg.status != "error",
                        "result": str(msg.content)[:400],
                    }
                )
        return by_view

    def _worth_reflecting(self, rec: dict, calls: list[dict]) -> bool:
        """Skip the LLM entirely when the run was routine for this view."""
        if any(not c["ok"] for c in calls):
            return True
        known = set(rec.get("params", {}))
        return any(set(c["params"]) - known for c in calls)

    def _merge(self, rec: dict, delta: dict) -> dict:
        params: dict[str, str] = dict(rec.get("params", {}))
        for name in delta.get("remove", []):
            params.pop(name, None)
        for name, note in (delta.get("params") or {}).items():
            params.pop(name, None)  # re-insert at the end: LRU eviction order
            params[name] = str(note)[: self.max_note_chars]
        if len(params) > self.max_params:
            params = dict(list(params.items())[-self.max_params :])

        out = {"params": params}
        if req := delta.get("required", rec.get("required")):
            out["required"] = sorted(set(req))
        return out

    async def _reflect_one(self, store, view: str, calls: list[dict]) -> None:
        rec = await self._load(store, view)
        if not self._worth_reflecting(rec, calls):
            return
        resp = await self.reflector.ainvoke(
            REFLECT_PROMPT.format(
                view=view,
                current=json.dumps(rec) or "{}",
                calls=json.dumps(calls, default=str),
                max_chars=self.max_note_chars,
            )
        )
        raw = resp.text() if hasattr(resp, "text") else str(resp.content)
        raw = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        try:
            delta = json.loads(raw)
        except json.JSONDecodeError:
            return  # keep the old record rather than corrupt it
        if delta:
            await self._save(store, view, self._merge(rec, delta))

    async def aafter_agent(self, state: dict, runtime: Any) -> None:
        by_view = self._mrx_calls(state.get("messages", []))
        if by_view:
            await asyncio.gather(
                *(self._reflect_one(runtime.store, v, c) for v, c in by_view.items() if v)
            )
        return None


# --------------------------------------------------------------------- wiring

async def build_agent():
    client = MultiServerMCPClient({"mrx": {"transport": "http", "url": "http://localhost:8000/mcp"}})
    tools = await client.get_tools()

    return create_agent(
        model="anthropic:claude-sonnet-4-6",
        tools=tools,
        system_prompt=(
            "Answer using the available tools. Budget: 5 tool calls per question. "
            f"When you call {TOOL_NAME}, notes learned from earlier runs against that "
            "view are attached to the first result — follow them."
        ),
        middleware=[
            ToolCallLimitMiddleware(run_limit=5, exit_behavior="end"),
            MrxViewMemory(),
        ],
        checkpointer=InMemorySaver(),
        store=InMemoryStore(),  # -> PostgresStore(...) in prod
    )


async def main() -> None:
    agent = await build_agent()
    result = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "Vega limit excesses on the FX desk yesterday?"}]},
        {"configurable": {"thread_id": "demo"}},
    )
    print(result["messages"][-1].content)


if __name__ == "__main__":
    asyncio.run(main())
