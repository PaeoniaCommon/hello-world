---
name: run-process
description: Run and test a toy_process Process, read its nested trace output, and fix common errors. Use after creating or changing any process in process_package.
---

# Run and test a Process

Run every command from `process_package/` so that `toy_process` and `examples`
can be imported.

## Run a process

```bash
cd process_package
python -m examples.word_report
```

Or from Python:

```python
from examples.word_report import WordReport

context = WordReport(text="a b a").run()   # keyword args override set_parameters
print(context)
```

`run()` prints a trace. `>` marks a process, `-` marks a method step, and
indentation shows nesting:

```
> WordReport
  - load_text
  > CleanText
    - strip_punctuation
    - normalise_case
  - count_words
  - build_report
```

Check that the trace matches the plan: the steps are in the right order and
the sub-processes are nested where intended.

## Run the tests

```bash
cd process_package
python -m unittest -v
```

All tests must pass, including the existing ones, before you finish.

## Common errors

| Error | Cause | Fix |
| --- | --- | --- |
| `TypeError: Can't instantiate abstract class ...` | `set_parameters` or `set_steps` missing | Define both in the child class |
| `TypeError: Invalid step ...` | A non-callable (string, `None`, result of `self.step()`) in `set_steps` | Use `self.step` or `SubProcess()` |
| `TypeError: Process.__init__() takes 1 positional argument ...` | A bare class `SubProcess` in `set_steps` | Use an instance: `SubProcess()` |
| `KeyError` on `context[...]` | A step reads a key no earlier step wrote | Reorder steps or write the key earlier |
| `KeyError` on `self.params[...]` | Parameter not in `set_parameters` | Add a default for it |
| `ModuleNotFoundError: toy_process` | Command run from the wrong folder | `cd process_package` first |
