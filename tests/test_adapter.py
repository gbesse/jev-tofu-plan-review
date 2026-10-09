import copy
import json
from pathlib import Path
import unittest

from app import adapt
from review_core import InputError, review
from jev import normalize


class AdapterTests(unittest.TestCase):
    def setUp(self):
        self.case = json.loads(Path("examples/case.json").read_text())
        self.policy = json.loads(Path("examples/policy.json").read_text())

    def test_value_free_summary_and_review_flag(self):
        self.case["plan"]["resource_changes"][0]["change"]["after"]["password"] = (
            "private-test-value"
        )
        parsed = adapt(self.case)
        self.assertNotIn("private-test-value", parsed["text"])
        self.assertIn("plan.resource_changes[1]", parsed["evidence"])
        result = review(
            self.case,
            self.policy,
            lambda _: normalize("aligned", 0.99, self.policy),
            adapt,
        )
        self.assertEqual(result["outcome"], "review")
        self.assertIn("destructive_change", result["flags"])
        self.assertFalse(result["automatic_action"])

    def test_rejects_unsupported_action_and_oversized_plan(self):
        bad = copy.deepcopy(self.case)
        bad["plan"]["resource_changes"][0]["change"]["actions"] = ["apply"]
        with self.assertRaises(InputError):
            adapt(bad)
        bad = copy.deepcopy(self.case)
        bad["plan"]["resource_changes"] *= 26
        with self.assertRaises(InputError):
            adapt(bad)


if __name__ == "__main__":
    unittest.main()
