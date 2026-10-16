---
name: create-process
description: Write a new Process subclass with the toy_process package (set_parameters, set_steps, step methods, nested sub-processes), plus its test. Use when building a process, workflow or pipeline in process_package, after planning it with design-process.
---

# Create a Process

All paths are relative to the repository root. The package is in
`process_package/`.

## How the parent class works

`process_package/toy_process/process.py` defines `Process`:

- `__init__(**overrides)` sets `self.params = {**self.set_parameters(), **overrides}`,
  then `self.steps = self.set_steps()`.
- `set_parameters()` and `set_steps()` are abstract. A child missing either one
  cannot be instantiated.
- `run(context=None)` loops over `self.steps` in order:
  - a `Process` instance → `step.run(context)`, nested, with the **same** context dict
  - any other callable → `step(context)`
  - anything else → `TypeError`
- `run` returns the context dict and prints an indented trace.

Do not modify `toy_process/` or override `__init__` or `run` in a child.

## Rules for the child class

1. `from toy_process import Process` and subclass it.
2. `set_parameters(self)` returns a `dict` of defaults. Use `{}` if there are none.
3. `set_steps(self)` returns a `list`. Each item is either:
   - a bound method: `self.count_words`, with **no parentheses**, or
   - a Process **instance**: `CleanText(lowercase=self.params["lowercase"])`.
4. Each step method has the signature `def name(self, context):`.
   - Read settings from `self.params["..."]`.
   - Read and write data in `context["..."]`.
   - Return nothing. Return values are ignored.
5. Define a sub-process class above the class that uses it, or import it.

## Template

```python
"""One-line description of what the process does.

Run from process_package/:
    python -m examples.<module_name>
"""

from toy_process import Process


class SubTask(Process):
    def set_parameters(self):
        return {"option": True}

    def set_steps(self):
        return [self.do_part]

    def do_part(self, context):
        if self.params["option"]:
            context["value"] = context["value"] * 2


class MainTask(Process):
    def set_parameters(self):
        return {"start": 1, "option": True}

    def set_steps(self):
        return [
            self.load,
            SubTask(option=self.params["option"]),  # nested sub-process
            self.finish,
        ]

    def load(self, context):
        context["value"] = self.params["start"]

    def finish(self, context):
        context["result"] = f"value is {context['value']}"


if __name__ == "__main__":
    print(MainTask(start=5).run()["result"])
```

## Files to create

1. `process_package/examples/<module_name>.py`: the process, from the template.
2. `process_package/tests/test_<module_name>.py`: a `unittest` test that calls
   `.run()` and asserts on keys in the returned context. Also check that
   overriding a parameter changes the result.

```python
import unittest

from examples.<module_name> import MainTask


class MainTaskTests(unittest.TestCase):
    def test_run(self):
        self.assertEqual(MainTask(start=5).run()["result"], "value is 10")

    def test_parameter_override(self):
        self.assertEqual(MainTask(start=5, option=False).run()["result"], "value is 5")


if __name__ == "__main__":
    unittest.main()
```

Then verify with the `run-process` skill. A complete working example is
`process_package/examples/word_report.py`.
