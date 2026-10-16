"""Toy example: a MakeBreakfast process that nests a MakeToast sub-process.

Run from the process_package folder:
    python -m examples.breakfast
"""

from toy_process import Process


class MakeToast(Process):
    def set_parameters(self):
        return {"slices": 2}

    def set_steps(self):
        return [self.toast_bread, self.butter_toast]

    def toast_bread(self, context):
        context["toast"] = f"{self.params['slices']} slices of toast"

    def butter_toast(self, context):
        context["toast"] = "buttered " + context["toast"]


class MakeBreakfast(Process):
    def set_parameters(self):
        return {"drink": "coffee", "slices": 2}

    def set_steps(self):
        return [
            self.brew_drink,
            MakeToast(slices=self.params["slices"]),  # nested sub-process
            self.serve,
        ]

    def brew_drink(self, context):
        context["drink"] = f"a cup of {self.params['drink']}"

    def serve(self, context):
        context["breakfast"] = f"{context['drink']} and {context['toast']}"


if __name__ == "__main__":
    result = MakeBreakfast(drink="tea", slices=3).run()
    print(result["breakfast"])
