"""The Process parent class.

A Process is a named list of steps. Each step is either:

* a method on the process (called as ``step(context)``), or
* another Process (run as a nested sub-process, sharing the same context).

Children must define ``set_parameters`` and ``set_steps``.
"""

from abc import ABC, abstractmethod


class Process(ABC):
    def __init__(self, **overrides):
        # Defaults come from the child; keyword arguments override them.
        self.params = {**self.set_parameters(), **overrides}
        self.steps = self.set_steps()

    @abstractmethod
    def set_parameters(self):
        """Return a dict of default parameters for this process."""

    @abstractmethod
    def set_steps(self):
        """Return a list of steps: bound methods and/or Process instances."""

    def run(self, context=None, depth=0):
        """Run every step in order and return the shared context dict."""
        context = {} if context is None else context
        indent = "  " * depth
        print(f"{indent}> {type(self).__name__}")

        for step in self.steps:
            if isinstance(step, Process):
                step.run(context, depth + 1)
            elif callable(step):
                print(f"{indent}  - {step.__name__}")
                step(context)
            else:
                raise TypeError(f"Invalid step {step!r}: must be a method or a Process")

        return context
