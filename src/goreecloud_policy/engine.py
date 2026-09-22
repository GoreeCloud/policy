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


def _matches(request: PolicyRequest, rule: PolicyRule) -> bool:
    if (
        request.policy_id != rule.policy_id
        or request.policy_version != rule.policy_version
        or request.authority != rule.authority
    ):
        return False
    return all(_request_value(request, key) == expected for key, expected in rule.when.items())


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
