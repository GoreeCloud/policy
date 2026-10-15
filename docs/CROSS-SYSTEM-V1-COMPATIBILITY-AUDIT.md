# Policy v1 cross-system compatibility audit

**Status: BLOCKED — development review only.**  
**Review date:** 2026-10-15.  
**Canonical decision schema:** `contracts/policy-decision.schema.json` (Policy v1, `additionalProperties: false`).  
**Consumer source pins:** Manager and Privacy Shield use Policy revision `46071886da37a6566b69cc923005eef64cce2bcc`; Wardveil's Policy integration references the same contract revision.

## Verified source incompatibility

The canonical Policy v1 decision shape contains exactly twelve keys: `decision`, `policy_id`, `policy_version`, `authority`, `subject`, `resource`, `action`, `reason`, `matched_rule_ids`, `obligations`, `evaluated_at`, and `fresh`. The active development `PolicyResult.to_dict()` currently emits those twelve **plus** `scope` and `production_accepted`. Manager's `integrations/policy.py::validate_policy_decision` and Privacy Shield's `src/platform-policy-contract.mjs::validatePolicyDecisionEvidence` require the exact v1 shape and reject extra keys. Wardveil also documents exact v1 decision validation.

**Consequence:** Successful local evaluation and passing Policy unit tests do not imply compatibility with the source-contract consumers. Do not merge or promote this PR.

## Required corrective acceptance

1. Restore the exact twelve-field Policy v1 decision result in `PolicyResult.to_dict()` and the `/v1/evaluate` response. Do not change the v1 schema or widen consumers to accept unrelated fields.
2. Keep development-only/nonproduction status in `/healthz`, `/readyz`, or separate noncontract HTTP metadata; a Policy `allow` is decision evidence, not execution authority.
3. Replace any tests that expect `scope`/`production_accepted` in decision JSON with assertions of the exact canonical field set. Add HTTP contract conformance tests for `allow`, `deny`, `indeterminate`, and errors as applicable.
4. Verify compatibility with Manager and Privacy Shield source validators and Wardveil's v1 consumer before merge.
5. Complete identity-backed caller verification, signed rule provenance, freshness/distribution/enforcement gates and representative runtime qualification before any production acceptance.

**Execution note:** Attempts to patch the serializer directly were blocked by connected GitHub tool safety checks; no correction has been committed or verified. This record is an audit gate, not a certification or release approval.
