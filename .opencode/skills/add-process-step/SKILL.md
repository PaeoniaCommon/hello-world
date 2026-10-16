---
name: add-process-step
description: Add, remove or reorder steps in an existing toy_process Process, including nesting a sub-process inside it. Use when asked to extend or change an existing process in process_package.
---

# Change the steps of a Process

Steps run in the order of the list returned by `set_steps`. Read the existing
process file and its test first.

## Add a method step

1. Write a method with the signature `def my_step(self, context):`.
2. Add `self.my_step` (no parentheses) to the `set_steps` list where it should run.
3. If it needs a new setting, add a default for it in `set_parameters`.

```python
def set_steps(self):
    return [self.load, self.my_step, self.save]

def my_step(self, context):
    context["count"] = len(context["rows"])
```

## Add a nested sub-process step

1. Create or reuse a `Process` subclass with its own `set_parameters` and
   `set_steps` (see the `create-process` skill).
2. Add an **instance** of it to the parent's `set_steps`, passing parameters
   down as keyword arguments. If the parent should control a setting, add it
   to the parent's `set_parameters` too.

```python
def set_parameters(self):
    return {"min_length": 3}

def set_steps(self):
    return [
        self.load,
        CleanRows(min_length=self.params["min_length"]),  # runs nested
        self.save,
    ]
```

The sub-process shares the parent's `context`. Keys it writes are available to
later parent steps.

## Turn existing method steps into a sub-process

When several method steps belong together:

1. Move those methods into a new `Process` subclass, keeping their order in its
   `set_steps`.
2. Move the parameters they use into its `set_parameters`, and change
   `self.params[...]` lookups if names change.
3. Replace those methods in the parent's `set_steps` with one instance of the
   new class.

## Checks

- Never put a call (`self.my_step()`) or a bare class (`CleanRows`) in the
  list. Use a bound method (`self.my_step`) or an instance (`CleanRows()`).
- Every `context` key a step reads must be written by an earlier step.
- Update the test to cover the new behaviour, then follow the `run-process` skill.
