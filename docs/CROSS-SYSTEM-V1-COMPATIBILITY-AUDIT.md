# Policy v1 cross-system compatibility audit

**Status: SOURCE CONTRACT CHECK PASSED; live integration and production acceptance remain outstanding.**  
**Reviewed:** 2026-10-15  
**Authoritative contract:** `contracts/policy-decision.schema.json` (v1, `additionalProperties: false`)  
**Consumer pins:** Manager, Privacy Shield, and Wardveil refer to Policy contract revision `46071886da37a6566b69cc923005eef64cce2bcc`.

## Finding and correction

An earlier Development candidate emitted `scope` and `production_accepted` in `PolicyResult.to_dict()`, although the published v1 decision schema admits exactly these twelve keys: `decision`, `policy_id`, `policy_version`, `authority`, `subject`, `resource`, `action`, `reason`, `matched_rule_ids`, `obligations`, `evaluated_at`, and `fresh`. Manager's `validate_policy_decision` and Privacy Shield's `validatePolicyDecisionEvidence` reject extra fields.

**Corrective commit:** `04d14e83974c7585cd2fd3c3ccbe1059a0613ae7` removed the noncontract fields. Updated unit/HTTP assertions and the new schema-driven contract regression enforce exactly the canonical v1 keys.

**Verification:** exact-source GitHub CI succeeded at `813ffa6bf3186c0d51eacbfc5055b2841729be22`, running **34 tests**. The prior red contract-gate run is retained as evidence that the check detects the incompatible result shape. No v1 schema was widened.

## Remaining acceptance requirements

- Execute a consumer-level conformance exchange against Manager, Privacy Shield, and Wardveil at pinned/qualified revisions. Source/schema conformance alone does not establish a live interoperable service.
- Keep Development-only status in `/healthz`/`/readyz`, not the versioned decision payload. A Policy `allow` remains decision evidence and does not confer enforcement or execution authority.
- Qualify Identity-authenticated callers, trusted/signed rule provenance, freshness/distribution/enforcement, security/privacy boundaries, and target-environment recovery before production acceptance.

**No merge, deployment, external reviewer approval, or Stable qualification is claimed.**
