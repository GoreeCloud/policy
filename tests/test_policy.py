import unittest

from goreecloud_policy import Decision, PolicyRequest, PolicyRule, evaluate
from goreecloud_policy.runtime import health_payload, readiness_payload


class PolicyTests(unittest.TestCase):
    def request(self):
        return PolicyRequest.from_mapping({
            "policy_id": "privacy.export",
            "policy_version": "1",
            "authority": "privacy-shield",
            "subject": "service:test",
            "resource": "record:1",
            "action": "export",
            "context": {"purpose": "user-request"},
        })

    def rule(self, rule_id, decision, **when):
        return PolicyRule.from_mapping({
            "rule_id": rule_id,
            "policy_id": "privacy.export",
            "policy_version": "1",
            "authority": "privacy-shield",
            "when": when,
            "decision": decision,
            "reason": rule_id,
        })

    def test_matching_allow(self):
        result = evaluate(self.request(), [self.rule("allow-user-export", "allow", purpose="user-request")])
        self.assertEqual(Decision.ALLOW, result.decision)
        self.assertEqual(("allow-user-export",), result.matched_rule_ids)

    def test_no_match_is_indeterminate_not_allow(self):
        result = evaluate(self.request(), [self.rule("other", "allow", purpose="different")])
        self.assertEqual(Decision.INDETERMINATE, result.decision)

    def test_conflict_is_indeterminate(self):
        result = evaluate(self.request(), [
            self.rule("allow", "allow", purpose="user-request"),
            self.rule("deny", "deny", purpose="user-request"),
        ])
        self.assertEqual(Decision.INDETERMINATE, result.decision)

    def test_rule_authority_must_match(self):
        rule = PolicyRule.from_mapping({
            "rule_id": "wrong-authority",
            "policy_id": "privacy.export",
            "policy_version": "1",
            "authority": "wardveil-security",
            "when": {"purpose": "user-request"},
            "decision": "allow",
        })
        self.assertEqual(Decision.INDETERMINATE, evaluate(self.request(), [rule]).decision)

    def test_invalid_decision_rejected(self):
        with self.assertRaises(ValueError):
            self.rule("bad", "maybe", purpose="user-request")

    def test_health_and_readiness_are_not_production_claims(self):
        self.assertEqual("healthy", health_payload()["status"])
        self.assertFalse(readiness_payload()["production_accepted"])


if __name__ == "__main__":
    unittest.main()
