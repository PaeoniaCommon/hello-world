---
name: design-process
description: Plan a new toy_process Process from a plain-language goal by breaking it into ordered steps and nested sub-processes. Use first whenever the user asks for a new process, workflow or pipeline, before writing any code.
---

# Design a Process

Use this skill to turn a request such as "make a process that counts the words
in some text" into a step plan. Then build it with the `create-process` skill.

The package lives in `process_package/`. The parent class is
`process_package/toy_process/process.py`.

## 1. List the steps

Write the goal as an ordered list of small actions, each a verb phrase:

```
WordReport
  1. clean the text
  2. count the words
  3. build the report
```

Each step should do one thing and put its result in the shared `context` dict.

## 2. Decide what each step is

For every step, choose:

| Use a **method step** when... | Use a **sub-process step** when... |
| --- | --- |
| it is one small action | it is several actions that belong together |
| it is only used here | it could be reused in other processes |
| it needs no settings of its own | it has its own parameters |

Sub-processes can contain sub-processes. Keep nesting shallow: two levels is
plenty for most toy processes.

## 3. Write the plan down

For each process (parent and every sub-process), record:

- **Class name**: a noun or verb phrase in `CamelCase`, e.g. `CleanText`.
- **Parameters**: name → default value. These go in `set_parameters`.
- **Steps**: in order. Methods are `snake_case`; sub-processes use their class name.
- **Context keys**: what each step reads and writes.

Example plan:

```
CleanText            params: lowercase=True
  - strip_punctuation  reads text   writes text
  - normalise_case     reads text   writes text

WordReport           params: text="", lowercase=True, top_n=3
  - load_text          reads -       writes text
  - CleanText(lowercase=...)   (sub-process)
  - count_words        reads text   writes counts
  - build_report       reads counts writes report
```

## 4. Check the plan

- Every context key a step reads is written by an earlier step.
- Every parameter a step uses is in that process's parameters.
- A sub-process gets its parameters passed in from the parent as keyword
  arguments, e.g. `CleanText(lowercase=self.params["lowercase"])`.

Show the plan to the user if the request was vague, then follow the
`create-process` skill.
