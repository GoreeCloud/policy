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

Development rule matching distinguishes absent context fields from explicitly present JSON null. Missing context cannot satisfy a nullable exact-match condition; explicit null remains matchable. Duplicate JSON keys and non-finite constants are rejected at loopback HTTP evaluation. These are source-only safeguards, not production rule-distribution or decision authority.

Development parser rejects overflowing exponent floats; rule matching compares JSON boolean conditions without integer/boolean aliasing, including nested values.

Solo-maintainer review: omitted `rule.when` is rejected; an explicitly provided empty object retains intentional broad-match semantics. Excessively nested JSON is rejected as HTTP 400 rather than causing an unhandled decoder recursion error. This remains a Development-only evaluator with no trusted external policy-provider integration.

### Development HTTP request boundary — 2026-10-15

Local-only API Host validation rejects DNS-rebinding Host aliases, browser Origin headers, and non-JSON POST media types. Existing local JSON requests still operate, and synthetic HTTP regressions cover all three rejections.

### Concurrent stabilization audit — 2026-10-15

Development API JSON responses now include Cache-Control: no-store and X-Content-Type-Options: nosniff; local HTTP regression verifies the response headers.

### Source-stabilization checkpoint — 2026-10-15

Loopback HTTP framing now rejects duplicate Host or Content-Length headers, Transfer-Encoding, malformed lengths and cross-site browser metadata. Synthetic negative requests fail before evaluation, while an authorized-looking but untrusted local test rule can still be evaluated in the Development reference runtime. No production rule provenance is established.
