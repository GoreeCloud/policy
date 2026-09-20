# GoreeCloud Policy Runtime Contract

## Document metadata

- **Status:** Draft
- **Version:** v0.1
- **Contract identifier:** `goreecloud.policy/0.1`
- **Last updated:** September 16, 2026
- **Classification:** Internal
- **Repository:** `GoreeCloud/policy`
- **Platform Contract baseline:** `0.4`
- **Integral Platform System authority:** `Instructions — Integral Platform Systems v3.0`
- **Implementation status:** Contract foundation only; this document does not claim a deployed or accepted production runtime.

## 1. Purpose

GoreeCloud Policy provides the common machinery for policy representation, evaluation, decision generation, distribution, enforcement coordination, explanation, versioning, provenance, freshness, conflict handling, simulation, and policy evidence across GoreeCloud.

This contract defines the first common runtime boundary for that machinery. It exists so applications, services, Integral Platform Systems, enforcement points, GoreeCloud Mesh, GoreeCloud Manager, and evidence consumers can exchange policy requests and decisions without inventing incompatible local semantics.

GoreeCloud Policy is a policy decision authority and shared evaluation framework. It is **not** the substantive owner of every rule it evaluates.

## 2. Authority boundaries

Policy ownership and policy evaluation are separate responsibilities.

- **Privacy Shield** owns privacy meaning, consent requirements, purpose limitation, collection/use/sharing restrictions, retention requirements, telemetry privacy, tracking rules, and other privacy-domain rules.
- **Wardveil Security** owns security meaning, trust posture, risk, threat handling, defensive requirements, and security-domain rules.
- **GoreeCloud Identity** owns identity facts, authentication state, claims, sessions, workload identity, and authoritative identity context.
- **Everkeep** owns continuity, preservation, recoverability, portability, succession, and related continuity requirements.
- **GoreeCloud Manager** owns administrative control, management-plane actions, and authorized administration boundaries.
- Other approved GoreeCloud systems remain authoritative for rules within their documented domains.

GoreeCloud Policy may normalize, evaluate, compose, distribute, explain, simulate, and coordinate enforcement of those rules under approved contracts. Evaluation does not transfer ownership.

A Policy decision must preserve enough provenance to identify the authority that owns each material rule or input used to reach the decision.

## 3. Core operating principles

1. **Explicit context.** Evaluation operates on an explicit actor, action, resource, purpose, environment, requested policy set, and authoritative inputs.
2. **Versioned policy.** Every evaluated policy definition has a stable identifier and version.
3. **Attributable authority.** Every material rule identifies its owning GoreeCloud authority.
4. **Fail closed.** Missing, stale, conflicting, unverifiable, unavailable, or unauthenticated required authority input never becomes an implicit `allow`.
5. **No authority laundering.** Aggregation, transport, caching, UI presentation, or enforcement does not change the source authority of a rule or fact.
6. **Evidence-backed enforcement.** Enforcement points must be able to record what decision they enforced, when, under which policy/version, and with what result.
7. **Purpose minimization.** Evaluation and evidence exchange must not disclose more user, device, security, or operational context than the decision requires.
8. **Deterministic semantics.** The same authoritative policy snapshot and relevant input set should produce the same decision unless the contract explicitly declares time-, randomness-, or external-state-dependent behavior.
9. **Simulation isolation.** Dry-run or simulation evaluation never authorizes or performs a production mutation.
10. **Truthful state.** `unknown`, `indeterminate`, stale, partial, blocked, failed, or error states are represented explicitly rather than being normalized into success.

## 4. Policy definition model

A policy definition is an immutable versioned envelope once promoted for use. The canonical machine-readable shape is defined by [`schemas/policy.definition.schema.json`](schemas/policy.definition.schema.json).

A policy definition identifies at minimum:

- policy identifier;
- policy version;
- owning authority;
- lifecycle state;
- description and scope;
- supported actions and resource classes;
- evaluation mode;
- precedence and composition metadata when applicable;
- override/exception rules when applicable;
- freshness and expiry requirements;
- rule set or evaluator reference;
- effective and optional expiration timestamps.

Policy definitions may reference domain-owned rules instead of copying their full sensitive contents. Where references are used, the reference must be resolvable and versioned sufficiently to reproduce or audit the evaluation.

### 4.1 Lifecycle

Contract `v0.1` uses these policy-definition lifecycle values:

- `draft`
- `under-review`
- `active`
- `deprecated`
- `retired`

Only `active` definitions are eligible for ordinary production enforcement unless an explicitly authorized transition or rollback procedure says otherwise.

### 4.2 Evaluation modes

A definition declares one of:

- `enforcing` — decisions may be used by production enforcement points.
- `advisory` — decisions are informational and cannot by themselves authorize or deny a mutation.
- `simulation` — evaluation is isolated from production enforcement and is used for testing, preview, migration, or impact analysis.

A caller or enforcement point must not reinterpret `advisory` or `simulation` output as an enforcing decision.

## 5. Evaluation request model

The canonical request shape is [`schemas/policy.evaluation-request.schema.json`](schemas/policy.evaluation-request.schema.json).

An evaluation request contains:

- contract version;
- globally unique request ID;
- request timestamp;
- caller/application/service identity reference;
- actor or subject identity reference when applicable;
- action;
- resource descriptor;
- declared purpose;
- environment/scope;
- requested policy identifiers or policy-set reference;
- authoritative input references;
- optional bounded context;
- optional correlation/trace identifier;
- requested evaluation mode.

### 5.1 Authority inputs

Authority inputs are facts or decisions supplied by systems that own them. Examples include Identity authentication state, Privacy Shield purpose/consent state, Wardveil risk state, Everkeep continuity requirements, or Manager administrative approval state.

Each authoritative input must carry or reference:

- source authority;
- source record or evidence identifier;
- source version/revision when applicable;
- observation/evaluation time;
- freshness or expiry boundary when applicable;
- integrity/provenance information required by the consuming scope.

The Policy runtime must not silently fabricate a missing authority input.

## 6. Decision model

The canonical decision envelope is [`schemas/policy.decision.schema.json`](schemas/policy.decision.schema.json).

A decision records:

- contract version;
- decision ID and request ID;
- evaluation mode;
- outcome;
- evaluated policy/version set;
- owning authorities involved;
- evaluation timestamp;
- validity/freshness bounds;
- reasons and explanation references;
- conditions or obligations where applicable;
- unresolved/missing inputs where applicable;
- enforcement guidance;
- evidence references;
- correlation identifier where applicable.

### 6.1 Decision outcomes

#### `allow`

All required policy evaluation completed successfully and the requested action is permitted within the stated scope and validity window. An `allow` must not be emitted when a required authority input is missing, stale beyond its allowed freshness, unverifiable, or in conflict unless the applicable active policy explicitly defines a safe resolution.

#### `deny`

The requested action is not permitted under the evaluated enforcing policy. The decision must identify the material policy/reason references required for audit and appropriate explanation without exposing protected information.

#### `conditional`

The action is not yet unconditionally permitted. One or more explicit conditions or obligations must be satisfied before an enforcement point may treat the operation as allowed. Completion of conditions must be evidenced or re-evaluated as the contract requires.

#### `defer`

This Policy evaluation intentionally delegates the final decision to a named authority, decision point, or later phase. `defer` is not `allow` and must not be interpreted as one.

#### `indeterminate`

The Policy runtime cannot produce a trustworthy substantive decision because required inputs are missing, stale, conflicting, unknown, unverifiable, unsupported, or otherwise insufficient. `indeterminate` is fail-closed for any operation requiring an affirmative policy decision.

#### `error`

A technical or internal evaluation failure prevented a valid policy decision. `error` is never an implicit `allow`. Callers may retry only when the returned error classification indicates retry is appropriate.

## 7. Freshness and validity

Policy evaluation is time-sensitive when underlying facts or rules are time-sensitive.

Decision freshness states are:

- `current`
- `stale`
- `unknown`

A decision may include `valid_until`. An enforcement point must not use a decision after its validity window for an operation that requires current authorization.

If the runtime knows that a required policy definition or authority input has changed since evaluation, the previous decision must not be represented as current.

Caching is allowed only when the active policy explicitly permits it and the cache key includes all context necessary to prevent cross-user, cross-resource, cross-purpose, or cross-environment decision leakage.

## 8. Composition, precedence, and conflicts

GoreeCloud Policy does not impose one universal precedence rule across every domain.

Composition behavior must be explicit in the active policy set. Supported composition modes may include:

- all-required;
- any-required;
- priority-ordered;
- domain-owner-final;
- explicit custom composition implemented by an approved evaluator.

A definition may mark a rule as non-overridable where the owning authority permits that semantic.

If two required authoritative rules conflict and no active approved precedence/composition rule resolves the conflict, the outcome must be `indeterminate`, not an invented success.

### 8.1 Overrides and exceptions

Overrides and exceptions must be explicit, bounded, attributable, and auditable. They must include:

- approving authority;
- reason;
- scope;
- affected policy/rule;
- creation time;
- expiry or review boundary;
- actor/service authorized to use the exception;
- evidence reference.

An override cannot grant broader authority than the authority approving it possesses.

## 9. Runtime interfaces

Contract `v0.1` defines logical interfaces, not deployed URLs.

### 9.1 Evaluate

Accepts a policy evaluation request and returns one policy decision.

### 9.2 Simulate

Evaluates a request in `simulation` mode and returns a decision that cannot authorize production enforcement.

### 9.3 Resolve policy set

Returns the versioned policy definitions applicable to an explicit context or policy-set identifier, subject to authorization.

### 9.4 Distribute policy state

Publishes or makes available current approved policy definitions, versions, invalidations, and lifecycle changes to authorized evaluators/caches.

### 9.5 Register enforcement evidence

Accepts enforcement-result evidence conforming to [`schemas/policy.enforcement-evidence.schema.json`](schemas/policy.enforcement-evidence.schema.json).

### 9.6 Explain decision

Returns an authorized explanation or explanation reference for a decision without exposing unnecessary secrets, private attributes, security-sensitive rule internals, or protected implementation detail.

Concrete transports may be HTTP, RPC, message/event, local library/IPC, or another approved mechanism. Transport does not change the decision semantics in this contract.

## 10. Enforcement coordination

A policy enforcement point must:

- verify that the decision applies to the same action/resource/subject/purpose context;
- verify decision integrity/provenance as required by its trust boundary;
- verify the decision is within its validity window;
- reject or re-evaluate stale decisions where current authorization is required;
- satisfy and evidence all mandatory conditions before enforcing a `conditional` decision as allowed;
- never treat `defer`, `indeterminate`, or `error` as `allow`;
- record enforcement evidence when governance requires it;
- preserve the decision ID and relevant policy/version references.

An enforcement point may apply stricter local safety controls but must not weaken an authoritative deny or required condition without an authorized exception contract.

## 11. Enforcement evidence

The enforcement evidence schema records:

- evidence ID;
- decision ID and request ID;
- enforcement-point identity;
- owning application/service;
- requested action/resource reference;
- decision outcome presented to the enforcement point;
- actual enforcement result;
- enforcement timestamp;
- policy/version references;
- conditions satisfied or unsatisfied;
- reason/status;
- evidence provenance/correlation references.

Enforcement results are one of:

- `allowed`
- `denied`
- `blocked-condition-unsatisfied`
- `deferred`
- `not-enforced`
- `failed`

Evidence must describe what happened. It must not rewrite the original policy decision.

## 12. Explanation requirements

Explanations should identify the governing policy and meaningful reason while minimizing disclosure.

A user-facing explanation may be less detailed than an authorized audit explanation. The decision envelope may therefore carry reason codes and explanation references rather than unrestricted policy internals.

Explanations must not reveal:

- credentials or secrets;
- sensitive security-detection logic when disclosure creates risk;
- unrelated private attributes;
- hidden data from another user/tenant;
- protected administrative context not authorized for the recipient.

## 13. Privacy, security, and identity constraints

- Privacy Shield controls what personal or telemetry data Policy may collect, retain, correlate, expose, or include in evidence.
- Wardveil Security controls trust and protection requirements for evaluators, caches, policy distribution, enforcement points, and evidence channels.
- GoreeCloud Identity supplies authoritative actor/service/device/workload identity context. Policy does not mint identity facts merely to complete evaluation.
- Sensitive context should be referenced by stable protected identifiers when full values are unnecessary.
- Policy logs/evidence must support retention limits, access control, export/deletion obligations where applicable, and least privilege.

## 14. GoreeCloud Mesh, Manager, and Observability

**GoreeCloud Mesh** may advertise Policy capabilities, route requests/events, publish version relationships, and carry evidence references. Mesh does not create policy authorization.

**GoreeCloud Manager** may administer policy lifecycle, expose approved management controls, display decisions/evidence, and initiate authorized changes. Manager does not become the policy evaluator merely because it presents the controls.

**GoreeCloud Observability** may observe evaluator availability, latency, error rates, policy-distribution freshness, enforcement failures, and other operational signals. Observability must preserve Policy outcome semantics and cannot infer `allow` from absence of observed denial.

## 15. Failure semantics

The runtime must classify failures sufficiently for callers to distinguish at least:

- invalid request;
- unsupported policy/contract version;
- policy not found;
- policy inactive/retired;
- required authority input missing;
- stale required input;
- conflicting policy;
- authorization failure;
- integrity/provenance failure;
- evaluator unavailable;
- timeout;
- internal error.

Failures that prevent trustworthy policy evaluation produce `indeterminate` or `error` as appropriate. They do not produce `allow` merely to preserve availability.

## 16. Versioning and compatibility

- Contract version `0.1` is the initial draft runtime contract.
- Backward-compatible additions may be introduced within a later compatible revision only when consumers can safely ignore them under the governing schema/version rules.
- Breaking changes require a new contract version and migration guidance.
- Policy definitions carry their own policy versions independently of this runtime contract version.
- Evidence must retain the contract version and policy versions used when the event occurred.
- Historical decisions must not be silently reinterpreted under a newer contract.

## 17. Required acceptance before v1.0 approval

Promotion of this contract to an approved `v1.0` requires authoritative evidence that at minimum:

- the schemas are valid and examples validate;
- decision outcomes and fail-closed semantics are covered by tests;
- policy ownership/evaluation boundaries are reviewed against all nine Integral Platform Systems;
- request, decision, and enforcement-evidence compatibility is demonstrated;
- freshness, stale-input, conflict, exception, and simulation behavior is tested;
- privacy/minimization and security constraints are validated;
- at least one real evaluator and one enforcement point implement the contract in a controlled environment;
- exact-revision evidence is retained;
- the repository Platform Contract declaration is updated truthfully from its then-current implementation state.

A passing document/schema CI job alone does not satisfy these runtime acceptance conditions.

## 18. Revision history

| Version | Date | Status | Change |
|---|---|---|---|
| v0.1 | September 16, 2026 | Draft | Initial shared GoreeCloud Policy runtime contract defining authority boundaries, definition/request/decision models, outcomes, freshness, composition, enforcement coordination, evidence, failure semantics, and v1.0 acceptance requirements. |
