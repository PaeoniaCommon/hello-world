---
name: add-process-step
description: Add a step (a method or a nested sub-process) to an existing toy_process Process subclass. Use when asked to extend, insert into or nest something inside an existing process.
---

# Add a step to a Process

Steps run in the order they appear in the list returned by `set_steps`.

## Option A: add a method step

1. Write a method on the class with the signature `def my_step(self, context):`.
2. Add `self.my_step` (no parentheses) to the list in `set_steps` at the
   position where it should run.
3. If it needs a new setting, add a default for it in `set_parameters`.

```python
def set_steps(self):
    return [self.load, self.my_step, self.save]

def my_step(self, context):
    context["count"] = len(context["rows"])
```

## Option B: add a nested sub-process step

1. Create (or reuse) a `Process` subclass with its own `set_parameters` and
   `set_steps` (see the `create-process` skill).
2. Add an **instance** of it to the parent's `set_steps` list, passing any
   parameter overrides as keyword arguments.

```python
def set_steps(self):
    return [
        self.load,
        CleanRows(min_length=self.params["min_length"]),  # runs nested
        self.save,
    ]
```

The sub-process reads and writes the same `context` dict as the parent, so
keys it sets are available to later parent steps.

## Checks

- Never put a call (`self.my_step()`) or a class (`CleanRows`) in the list;
  use a bound method (`self.my_step`) or an instance (`CleanRows()`). Anything
  else raises `TypeError` at run time.
- Make sure each step's required `context` keys are set by an earlier step.
- Run the tests (see the `run-process` skill).
