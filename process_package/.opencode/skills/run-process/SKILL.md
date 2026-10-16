---
name: run-process
description: Run and test a toy_process Process, and read its nested trace output. Use after creating or changing a process to verify it works.
---

# Run and test a Process

All commands run from the `process_package/` folder so `toy_process` is importable.

## Run a process

```bash
python -m examples.breakfast
```

Or from Python:

```python
from examples.breakfast import MakeBreakfast

context = MakeBreakfast(drink="tea").run()   # keyword args override set_parameters
print(context)
```

`run()` prints a trace. `>` marks a process, `-` marks a method step, and
indentation shows nesting:

```
> MakeBreakfast
  - brew_drink
  > MakeToast
    - toast_bread
    - butter_toast
  - serve
```

Use the trace to confirm the steps ran in the expected order and that
sub-processes are nested where intended.

## Run the tests

```bash
python -m unittest -v
```

## Common errors

| Error | Cause | Fix |
| --- | --- | --- |
| `TypeError: Can't instantiate abstract class ...` | `set_parameters` or `set_steps` missing | Define both in the child class |
| `TypeError: Invalid step ...` | A non-callable (string, class result, `None`) in `set_steps` | Use `self.method` or `SubProcess()` |
| `KeyError` in a step | A step reads a `context` key no earlier step set | Reorder steps or set the key earlier |
| `KeyError` on `self.params[...]` | Parameter not in `set_parameters` | Add a default for it |
