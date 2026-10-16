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
├── examples/breakfast.py      # MakeBreakfast nests a MakeToast sub-process
├── tests/test_process.py
└── .opencode/skills/          # agent skills (opencode / Claude Code compatible)
    ├── create-process/SKILL.md
    ├── add-process-step/SKILL.md
    └── run-process/SKILL.md
```

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

The `.opencode/skills/` folder holds `SKILL.md` files that an agent such as
opencode discovers when started in `process_package/`. They teach it how to
create a process, add steps or sub-processes, and run and test the result.
