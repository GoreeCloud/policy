"""Fail-closed regression for the published Policy v1 decision contract."""
import json
import unittest
from pathlib import Path

from goreecloud_policy import PolicyRequest, PolicyRule, evaluate


class PolicyV1ContractTests(unittest.TestCase):
    def test_evaluation_result_has_exact_published_decision_fields(self):
        root = Path(__file__).resolve().parents[1]
        schema = json.loads((root / "contracts" / "policy-decision.schema.json").read_text())
        request = PolicyRequest.from_mapping({
            "policy_id": "privacy.export", "policy_version": "1",
            "authority": "privacy-shield", "subject": "service:tester",
            "resource": "synthetic:record", "action": "read",
            "context": {"purpose": "review"},
        })
        rule = PolicyRule.from_mapping({
            "rule_id": "review-only", "policy_id": "privacy.export",
            "policy_version": "1", "authority": "privacy-shield",
            "when": {"purpose": "review"}, "decision": "allow",
        })
        result = evaluate(request, [rule]).to_dict()
        self.assertFalse(schema["additionalProperties"])
        self.assertEqual(set(schema["required"]), set(schema["properties"]))
        self.assertEqual(
            set(schema["properties"]), set(result),
            "Policy v1 clients reject additional/missing decision fields",
        )


if __name__ == "__main__":
    unittest.main()
