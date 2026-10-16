import unittest

from examples.breakfast import MakeBreakfast, MakeToast
from toy_process import Process


class ProcessTests(unittest.TestCase):
    def test_runs_methods_and_nested_process(self):
        result = MakeBreakfast(drink="tea", slices=3).run()
        self.assertEqual(result["breakfast"], "a cup of tea and buttered 3 slices of toast")

    def test_default_parameters(self):
        self.assertEqual(MakeToast().params, {"slices": 2})

    def test_child_must_define_set_steps_and_set_parameters(self):
        class Incomplete(Process):
            def set_parameters(self):
                return {}

        with self.assertRaises(TypeError):
            Incomplete()

    def test_invalid_step_raises(self):
        class Bad(Process):
            def set_parameters(self):
                return {}

            def set_steps(self):
                return ["not a step"]

        with self.assertRaises(TypeError):
            Bad().run()


if __name__ == "__main__":
    unittest.main()
