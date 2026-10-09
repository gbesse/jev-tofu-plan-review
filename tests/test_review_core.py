import json
from pathlib import Path
import unittest

from jev import normalize
from review_core import InputError, review


class ReviewCoreTests(unittest.TestCase):
    def setUp(self):
        self.policy = json.loads(Path("examples/policy.json").read_text())
        self.choice = next(key for key in self.policy["criteria"] if key != "other")
        self.case = {
            "subject": "test",
            "text": "A bounded synthetic case",
            "evidence": ["case.text"],
            "flags": [],
        }

    def test_threshold_and_hard_flag(self):
        result = review(
            self.case,
            self.policy,
            lambda _: normalize(self.choice, 0.99, self.policy),
            lambda value: value,
        )
        self.assertEqual(result["outcome"], self.choice)
        flagged = {**self.case, "flags": ["manual_review_required"]}
        result = review(
            flagged,
            self.policy,
            lambda _: normalize(self.choice, 0.99, self.policy),
            lambda value: value,
        )
        self.assertEqual(result["outcome"], "review")
        self.assertFalse(result["automatic_action"])

    def test_rejects_invalid_case_and_decision(self):
        with self.assertRaises(InputError):
            review(
                {**self.case, "text": ""},
                self.policy,
                lambda _: {},
                lambda value: value,
            )
        with self.assertRaises(InputError):
            review(
                self.case,
                self.policy,
                lambda _: {"choice": "invalid"},
                lambda value: value,
            )


if __name__ == "__main__":
    unittest.main()
