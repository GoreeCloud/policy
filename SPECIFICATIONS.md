# GoreeCloud Policy — Specifications

## Scope

This Development foundation defines a deterministic policy-decision boundary. It does not replace the domain authority of Privacy Shield, Wardveil Security, GoreeCloud Identity, Everkeep, GoreeCloud Manager, or another approved authority.

## Evaluation request

A request identifies a policy, version, rule authority, subject, resource, action, and bounded context. Required string identifiers must be non-empty. Context must be a JSON object.

## Rule model

A rule contains the same policy identity/version/authority, a `when` object, a decision, an optional reason, and optional obligations. `when` keys can match `subject`, `resource`, `action`, or keys in request context. Matching is exact in this foundation.

## Decision integrity

- No matching rule => `indeterminate`.
- All matching rules agree => that decision.
- Matching rules disagree => `indeterminate` with conflict reason.
- Invalid decision or malformed input => request rejected or `error` at the runtime boundary.
- A deny, unknown, stale, malformed, or conflicting result is never converted to allow.

## Evidence

Each result preserves policy ID/version, rule authority, subject/resource/action, result, reason, evaluation timestamp, freshness flag, matched rule IDs, and obligations.

## Runtime

The reference service is local-development-only and provides:
- `GET /healthz`
- `GET /readyz`
- `POST /v1/evaluate`

The reference runtime does not persist requests or decisions and does not establish GoreeCloud Identity authentication, Mesh routing, production policy distribution, or production enforcement acceptance.
