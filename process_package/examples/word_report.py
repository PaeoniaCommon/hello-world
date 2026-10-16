"""Count the most common words in some text, cleaning it in a nested sub-process.

Run from process_package/:
    python -m examples.word_report
"""

import string
from collections import Counter

from toy_process import Process


class CleanText(Process):
    def set_parameters(self):
        return {"lowercase": True}

    def set_steps(self):
        return [self.strip_punctuation, self.normalise_case]

    def strip_punctuation(self, context):
        context["text"] = context["text"].translate(str.maketrans("", "", string.punctuation))

    def normalise_case(self, context):
        if self.params["lowercase"]:
            context["text"] = context["text"].lower()


class WordReport(Process):
    def set_parameters(self):
        return {"text": "", "lowercase": True, "top_n": 3}

    def set_steps(self):
        return [
            self.load_text,
            CleanText(lowercase=self.params["lowercase"]),  # nested sub-process
            self.count_words,
            self.build_report,
        ]

    def load_text(self, context):
        context["text"] = self.params["text"]

    def count_words(self, context):
        context["counts"] = Counter(context["text"].split())

    def build_report(self, context):
        top = context["counts"].most_common(self.params["top_n"])
        context["report"] = ", ".join(f"{word}={n}" for word, n in top)


if __name__ == "__main__":
    text = "The cat sat. The cat ran! A dog sat, the end."
    print(WordReport(text=text).run()["report"])
