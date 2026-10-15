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

    def test_allow_result_is_explicitly_development_only(self):
        result = evaluate(self.request(), [
            self.rule("allow-local", "allow", purpose="user-request")
        ]).to_dict()
        self.assertEqual("allow", result["decision"])
        expected = {
            "decision", "policy_id", "policy_version", "authority",
            "subject", "resource", "action", "reason", "matched_rule_ids",
            "obligations", "evaluated_at", "fresh",
        }
        self.assertEqual(expected, set(result))

    def test_no_match_is_indeterminate_not_allow(self):
        result = evaluate(self.request(), [self.rule("other", "allow", purpose="different")])
        self.assertEqual(Decision.INDETERMINATE, result.decision)

    def test_conflict_is_indeterminate(self):
        result = evaluate(self.request(), [
            self.rule("allow", "allow", purpose="user-request"),
            self.rule("deny", "deny", purpose="user-request"),
        ])
        self.assertEqual(Decision.INDETERMINATE, result.decision)

    def test_policy_identity_tuple_must_match(self):
        base = self.request()
        good_rule = self.rule("matching", "allow", purpose="user-request")
        for attr in ("policy_id", "policy_version", "authority"):
            with self.subTest(attr=attr):
                raw = {
                    "policy_id": base.policy_id,
                    "policy_version": base.policy_version,
                    "authority": base.authority,
                    "subject": base.subject,
                    "resource": base.resource,
                    "action": base.action,
                    "context": dict(base.context),
                }
                raw[attr] = "different"
                request = PolicyRequest.from_mapping(raw)
                self.assertEqual(Decision.INDETERMINATE, evaluate(request, [good_rule]).decision)

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

    def test_missing_nullable_context_does_not_authorize(self):
        rule = self.rule("null-tenant", "allow", tenant=None)
        self.assertEqual(Decision.INDETERMINATE, evaluate(self.request(), [rule]).decision)

    def test_explicit_nullable_context_matches(self):
        rule = self.rule("null-tenant", "allow", tenant=None)
        request = PolicyRequest.from_mapping({
            "policy_id": "privacy.export", "policy_version": "1",
            "authority": "privacy-shield", "subject": "service:test",
            "resource": "record:1", "action": "export",
            "context": {"tenant": None},
        })
        self.assertEqual(Decision.ALLOW, evaluate(request, [rule]).decision)

    def test_boolean_does_not_match_numeric_context(self):
        original = self.request()
        for actual, expected in ((True, 1), (False, 0), (1, True), (0, False)):
            with self.subTest(actual=actual, expected=expected):
                request = PolicyRequest.from_mapping({
                    "policy_id": original.policy_id,
                    "policy_version": original.policy_version,
                    "authority": original.authority,
                    "subject": original.subject,
                    "resource": original.resource,
                    "action": original.action,
                    "context": {"condition": actual},
                })
                result = evaluate(request, [self.rule("gated", "allow", condition=expected)])
                self.assertEqual(Decision.INDETERMINATE, result.decision)

    def test_nested_boolean_number_collision_does_not_match(self):
        original = self.request()
        request = PolicyRequest.from_mapping({
            "policy_id": original.policy_id,
            "policy_version": original.policy_version,
            "authority": original.authority,
            "subject": original.subject,
            "resource": original.resource,
            "action": original.action,
            "context": {"flags": [{"approved": True}]},
        })
        result = evaluate(request, [
            self.rule("nested", "allow", flags=[{"approved": 1}]),
        ])
        self.assertEqual(Decision.INDETERMINATE, result.decision)

    def test_matching_boolean_context_still_allows(self):
        original = self.request()
        request = PolicyRequest.from_mapping({
            "policy_id": original.policy_id,
            "policy_version": original.policy_version,
            "authority": original.authority,
            "subject": original.subject,
            "resource": original.resource,
            "action": original.action,
            "context": {"approved": True},
        })
        result = evaluate(request, [self.rule("boolean", "allow", approved=True)])
        self.assertEqual(Decision.ALLOW, result.decision)

    def test_missing_rule_conditions_are_rejected(self):
        raw = {
            "rule_id": "unintended-wildcard",
            "policy_id": "privacy.export",
            "policy_version": "1",
            "authority": "privacy-shield",
            "decision": "allow",
        }
        with self.assertRaisesRegex(ValueError, "explicitly provided"):
            PolicyRule.from_mapping(raw)

    def test_null_conditions_are_rejected(self):
        raw = {
            "rule_id": "null-conditions",
            "policy_id": "privacy.export",
            "policy_version": "1",
            "authority": "privacy-shield",
            "when": None,
            "decision": "allow",
        }
        with self.assertRaisesRegex(ValueError, "must be an object"):
            PolicyRule.from_mapping(raw)

    def test_explicit_empty_conditions_remain_deliberate(self):
        # Explicit {} retains documented unconditional matching semantics,
        # but missing conditions can no longer silently become a wildcard.
        rule = self.rule("explicitly-unconditional", "deny")
        result = evaluate(self.request(), [rule])
        self.assertEqual(Decision.DENY, result.decision)

    def test_invalid_decision_rejected(self):
        with self.assertRaises(ValueError):
            self.rule("bad", "maybe", purpose="user-request")

    def test_health_and_readiness_are_not_production_claims(self):
        self.assertEqual("healthy", health_payload()["status"])
        self.assertFalse(readiness_payload()["production_accepted"])


if __name__ == "__main__":
    unittest.main()
