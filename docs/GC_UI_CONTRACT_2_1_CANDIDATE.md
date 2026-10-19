# GoreeCloud Policy — GC UI Platform Contract 2.1 opt-in evaluation

**Effective design authority:** GoreeCloud UI (GC UI), [GoreeCloud/gc-ui](https://github.com/GoreeCloud/gc-ui), is Integral Platform System #5 of nine and permanently replaces Glaze and Glaze UI. The current GoreeCloud Policy reference service has no owned graphical interface.

**Change status:** A **shadow / candidate** Platform Contract 2.1 declaration, tested as nonconformant. This is *not* a migration of the canonical Platform Contract 0.4 manifest, not acceptance of the Lab lifecycle, and not installation of GC UI as a library dependency. Current source and runtime remain unchanged.

The [candidate manifest](../goreecloud.platform.v2.1.candidate.yaml) records:
- Nine Integral Platform Systems, slot five `gc_ui`.
- `gc_ui: not-applicable-justified` for the **current headless reference service** only, with concrete Policy documentation as evidence.
- No new Glaze imports, dependencies, package bridges or compatibility claims.
- All seven external system integrations still blocked, Policy's self-integration inapplicable, all production conformance gates unresolved.
- `lifecycle: lab` as a **conservative provisional translation for testing the 2.1 schema only**, not an approved lifecycle reclassification. Release evidence, tests, and qualification flags remain blocked/empty.

[The opt-in workflow](../.github/workflows/gc-ui-contract-2-1.yml) calls the independently versioned [central GC UI 2.1 reusable validator](https://github.com/GoreeCloud/GoreeCloud/blob/1499491159250d5f15dad4e2835fbeee2fda9ce9/.github/workflows/reusable-platform-manifest-v2-1.yml) at its **immutable verified commit**. It validates the exact PR head, schema, declared nonconformance, producer/evaluator revision provenance, and uploads the bounded result artifact. The existing [0.4 canonical declaration](../goreecloud.platform.yaml) and [legacy workflow](../.github/workflows/platform-contract.yml) are untouched and remain independently versioned.

**Required before any authoritative cutover:** Confirm the Policy service's appropriate lifecycle stage from authoritative governance; amend higher-priority Drive Markdown in place; complete all applicable platform integrations, source and runtime conformance, security, recovery, and release qualification; re-evaluate UI applicability if an owned dashboard/admin console/website is introduced; explicitly authorize and validate a new canonical manifest. A CI-green *declaration check* is not product conformity or approval to deploy.

The one-for-one nine-system decision and remaining migration obligations are tracked in [GC UI issue #13](https://github.com/GoreeCloud/gc-ui/issues/13).
