from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from .model import Decision, PolicyRequest, PolicyResult, PolicyRule


def _request_value(request: PolicyRequest, key: str) -> Any:
    if key == "subject":
        return request.subject
    if key == "resource":
        return request.resource
    if key == "action":
        return request.action
    return request.context.get(key)



def _json_values_match(actual: Any, expected: Any) -> bool:
    # Python treats True == 1 and False == 0. JSON policy input does not:
    # a numeric assertion cannot satisfy a boolean condition, or vice versa.
    if isinstance(actual, bool) or isinstance(expected, bool):
        return type(actual) is type(expected) and actual == expected
    if isinstance(actual, dict) and isinstance(expected, dict):
        return actual.keys() == expected.keys() and all(
            _json_values_match(actual[key], expected[key]) for key in actual
        )
    if isinstance(actual, list) and isinstance(expected, list):
        return len(actual) == len(expected) and all(
            _json_values_match(item, condition)
            for item, condition in zip(actual, expected)
        )
    return actual == expected


def _matches(request: PolicyRequest, rule: PolicyRule) -> bool:
    if (
        request.policy_id != rule.policy_id
        or request.policy_version != rule.policy_version
        or request.authority != rule.authority
    ):
        return False
    for key, expected in rule.when.items():
        if key not in {"subject", "resource", "action"} and key not in request.context:
            return False
        if not _json_values_match(_request_value(request, key), expected):
            return False
    return True


def _result(request: PolicyRequest, decision: Decision, reason: str, rules: list[PolicyRule]) -> PolicyResult:
    obligations = tuple(dict.fromkeys(item for rule in rules for item in rule.obligations))
    return PolicyResult(
        decision=decision,
        policy_id=request.policy_id,
        policy_version=request.policy_version,
        authority=request.authority,
        subject=request.subject,
        resource=request.resource,
        action=request.action,
        reason=reason,
        matched_rule_ids=tuple(rule.rule_id for rule in rules),
        obligations=obligations,
    )


def evaluate(request: PolicyRequest, rules: Iterable[PolicyRule]) -> PolicyResult:
    matched = [rule for rule in rules if _matches(request, rule)]
    if not matched:
        return _result(request, Decision.INDETERMINATE, "No applicable rule matched", [])

    decisions = {rule.decision for rule in matched}
    if len(decisions) != 1:
        return _result(
            request,
            Decision.INDETERMINATE,
            "Applicable rules produced conflicting decisions; explicit composition is required",
            matched,
        )

    decision = next(iter(decisions))
    reasons = [rule.reason.strip() for rule in matched if rule.reason.strip()]
    reason = "; ".join(reasons) if reasons else f"{len(matched)} applicable rule(s) agreed"
    return _result(request, decision, reason, matched)
