# GoreeCloud Policy

GoreeCloud Policy is the shared policy-definition, evaluation, decision, distribution, and enforcement-coordination foundation for GoreeCloud.

**Lifecycle:** Development  
**Foundation version:** `0.1.0-dev`  
**Platform Contract:** `0.4`  
**License:** `AGPL-3.0-or-later`

This repository now contains a bounded reference implementation of deterministic policy evaluation. It is intentionally **not** a production authorization service yet. Privacy Shield, Wardveil Security, GoreeCloud Identity, Everkeep, and other domain authorities retain ownership of the substantive facts and rules they produce.

## Current source capabilities

- Explicit decisions: `allow`, `deny`, `conditional`, `defer`, `indeterminate`, `error`.
- Rule-authority and policy-version provenance in every decision.
- Deterministic matching with conflict detection; conflicting decisions never become an implicit allow.
- Invalid, unsupported, or unmatched evaluations fail closed as non-allowing results.
- Local-only development HTTP runtime with `/healthz`, `/readyz`, and `/v1/evaluate`.
- Contract 0.4 declaration covering all nine Integral Platform Systems.
- Standard-library tests and CI.

## Run locally

```bash
python -m goreecloud_policy
```

The reference runtime binds to `127.0.0.1:8787` by default. Set `GOREECLOUD_POLICY_HOST` and `GOREECLOUD_POLICY_PORT` only in a controlled development environment. Non-loopback binding is intentionally rejected by the current foundation.

## Test

```bash
python -m unittest discover -s tests -v
```

## License

GoreeCloud Policy is licensed under `AGPL-3.0-or-later`. See `LICENSE`.

See `SPECIFICATIONS.md`, `IMPLEMENTED-FEATURES.md`, `PLANNED-FEATURES.md`, and `goreecloud.platform.yaml` for the current evidence boundary.

Tracking: #1
