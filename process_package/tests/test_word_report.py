import unittest

from examples.word_report import WordReport


class WordReportTests(unittest.TestCase):
    def test_run(self):
        result = WordReport(text="The cat sat. The cat ran! the end.").run()
        self.assertEqual(result["report"], "the=3, cat=2, sat=1")

    def test_parameter_override(self):
        result = WordReport(text="The cat. the cat.", lowercase=False, top_n=2).run()
        self.assertEqual(result["report"], "cat=2, The=1")


if __name__ == "__main__":
    unittest.main()
