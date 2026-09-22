# Security

Do not use the current reference runtime as an Internet-facing authorization service.

The Development server is restricted to loopback binding. It does not provide production authentication, authorization, durable secret storage, signing-key management, policy-distribution trust, or enforcement-point attestation.

Never place credentials, tokens, private keys, reusable secrets, or raw sensitive content in policy rules, examples, logs, issues, or test fixtures.

Security-sensitive production integration requires GoreeCloud Identity and Wardveil Security acceptance plus applicable GoreeCloud Policy enforcement evidence.
