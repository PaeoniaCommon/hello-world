---
name: create-process
description: Create a new Process subclass using the toy_process package (set_parameters, set_steps, step methods, nested sub-processes). Use when asked to build a new process, workflow or pipeline in process_package.
---

# Create a Process

A process is a subclass of `toy_process.Process`. It runs a list of steps in
order. Read `toy_process/process.py` (about 40 lines) before starting.

## Rules

1. Subclass `Process` from `toy_process`.
2. Define **both** of these, or the class cannot be instantiated:
   - `set_parameters(self)` → returns a `dict` of default parameters.
   - `set_steps(self)` → returns a `list` of steps.
3. Each step is one of:
   - a **bound method** of the class, e.g. `self.load_data` (no parentheses), or
   - a **Process instance**, e.g. `CleanData(threshold=0.5)`, which runs as a
     nested sub-process.
4. Every step method has the signature `def name(self, context):`.
   - Read parameters from `self.params[...]`.
   - Read and write shared results in the `context` dict. Do not return values;
     return values are ignored.
5. Sub-processes share the parent's `context`. Pass any parameters they need
   as keyword arguments when constructing them inside `set_steps`, e.g.
   `MakeToast(slices=self.params["slices"])`.
6. Do not override `__init__` or `run`.

## Template

```python
from toy_process import Process


class MyProcess(Process):
    def set_parameters(self):
        return {"name": "world"}

    def set_steps(self):
        return [
            self.first_step,
            # MySubProcess(option=self.params["name"]),  # optional nested process
            self.last_step,
        ]

    def first_step(self, context):
        context["greeting"] = f"hello {self.params['name']}"

    def last_step(self, context):
        context["result"] = context["greeting"].upper()


if __name__ == "__main__":
    print(MyProcess(name="opencode").run()["result"])
```

## Steps to follow

1. Decide the steps. If a group of steps is reusable or logically separate,
   make it its own Process and use it as a step (see the `add-process-step` skill).
2. Put the new file in `examples/` (or the location the user asks for).
   Define sub-processes above the process that uses them.
3. Add a test in `tests/` that calls `.run()` and checks keys in the returned context.
4. Verify with the `run-process` skill.

See `examples/breakfast.py` for a complete working example.
