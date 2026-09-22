# Implemented Features

The entries below describe source implementation only. They do not imply release, deployment, production, certification, or Stable acceptance.

## POL-FOUNDATION-001 — Decision model

Implemented explicit `allow`, `deny`, `conditional`, `defer`, `indeterminate`, and `error` decisions with provenance and freshness fields.

## POL-FOUNDATION-002 — Deterministic evaluator

Implemented exact-match rule evaluation. Conflicting applicable decisions resolve to `indeterminate`, never to an implicit allow.

## POL-FOUNDATION-003 — Development runtime

Implemented local-only `/healthz`, `/readyz`, and `/v1/evaluate` endpoints without persistence or production identity claims.

## POL-FOUNDATION-004 — Contract and CI baseline

Added Contract 0.4 nine-system declaration, unit tests, and GitHub Actions validation.
