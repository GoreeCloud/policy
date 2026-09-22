from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Mapping


class Decision(str, Enum):
    ALLOW = "allow"
    DENY = "deny"
    CONDITIONAL = "conditional"
    DEFER = "defer"
    INDETERMINATE = "indeterminate"
    ERROR = "error"


def _required_text(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value.strip()


@dataclass(frozen=True, slots=True)
class PolicyRequest:
    policy_id: str
    policy_version: str
    authority: str
    subject: str
    resource: str
    action: str
    context: Mapping[str, Any] = field(default_factory=dict)

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "PolicyRequest":
        if not isinstance(value, Mapping):
            raise ValueError("request must be an object")
        context = value.get("context", {})
        if not isinstance(context, Mapping):
            raise ValueError("context must be an object")
        return cls(
            policy_id=_required_text(value.get("policy_id"), "policy_id"),
            policy_version=_required_text(value.get("policy_version"), "policy_version"),
            authority=_required_text(value.get("authority"), "authority"),
            subject=_required_text(value.get("subject"), "subject"),
            resource=_required_text(value.get("resource"), "resource"),
            action=_required_text(value.get("action"), "action"),
            context=dict(context),
        )


@dataclass(frozen=True, slots=True)
class PolicyRule:
    rule_id: str
    policy_id: str
    policy_version: str
    authority: str
    when: Mapping[str, Any]
    decision: Decision
    reason: str = ""
    obligations: tuple[str, ...] = ()

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "PolicyRule":
        if not isinstance(value, Mapping):
            raise ValueError("rule must be an object")
        when = value.get("when", {})
        if not isinstance(when, Mapping):
            raise ValueError("rule.when must be an object")
        try:
            decision = Decision(value.get("decision"))
        except (TypeError, ValueError) as exc:
            raise ValueError("rule.decision is not supported") from exc
        obligations = value.get("obligations", [])
        if not isinstance(obligations, list) or not all(isinstance(item, str) for item in obligations):
            raise ValueError("rule.obligations must be a list of strings")
        return cls(
            rule_id=_required_text(value.get("rule_id"), "rule_id"),
            policy_id=_required_text(value.get("policy_id"), "policy_id"),
            policy_version=_required_text(value.get("policy_version"), "policy_version"),
            authority=_required_text(value.get("authority"), "authority"),
            when=dict(when),
            decision=decision,
            reason=str(value.get("reason", "")),
            obligations=tuple(obligations),
        )


@dataclass(frozen=True, slots=True)
class PolicyResult:
    decision: Decision
    policy_id: str
    policy_version: str
    authority: str
    subject: str
    resource: str
    action: str
    reason: str
    matched_rule_ids: tuple[str, ...] = ()
    obligations: tuple[str, ...] = ()
    evaluated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    fresh: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "decision": self.decision.value,
            "policy_id": self.policy_id,
            "policy_version": self.policy_version,
            "authority": self.authority,
            "subject": self.subject,
            "resource": self.resource,
            "action": self.action,
            "reason": self.reason,
            "matched_rule_ids": list(self.matched_rule_ids),
            "obligations": list(self.obligations),
            "evaluated_at": self.evaluated_at,
            "fresh": self.fresh,
        }
