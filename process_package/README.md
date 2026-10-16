# process_package

A toy Python package for building **processes**: a parent class, `Process`,
whose children list a series of steps to run.

- `set_parameters()` returns default parameters (override with keyword args).
- `set_steps()` returns the steps: methods on the class, or other `Process`
  instances, which run as nested sub-processes.
- `run()` executes the steps in order, passing one shared `context` dict
  through all of them, and returns it.

```
process_package/
├── toy_process/process.py     # the Process parent class
├── examples/
│   ├── breakfast.py           # MakeBreakfast nests a MakeToast sub-process
│   └── word_report.py         # WordReport nests a CleanText sub-process
└── tests/
```

The agent skills live at the repository root in `.opencode/skills/`.

## Try it

```bash
cd process_package
python -m examples.breakfast
python -m unittest -v
```

```
> MakeBreakfast
  - brew_drink
  > MakeToast
    - toast_bread
    - butter_toast
  - serve
a cup of tea and buttered 3 slices of toast
```

## Agent skills

The main goal of this folder is to let a coding agent such as opencode build
new processes. It finds the `SKILL.md` files in `.opencode/skills/` at the
repository root when started anywhere inside this repository:

| Skill | Use it to |
| --- | --- |
| `design-process` | turn a plain-language goal into ordered steps and sub-processes |
| `create-process` | write the Process classes and a test from that plan |
| `add-process-step` | add, reorder or nest steps in an existing process |
| `run-process` | run, test and debug a process from its trace |

Example prompt: *"Create a process that reads a list of numbers, removes
outliers in a sub-process, and reports the mean."*
