# GoreeCloud Policy — User Manual

This Development foundation is intended for developers and platform integrators.

## Start

```bash
python -m goreecloud_policy
```

The server listens on loopback only by default.

## Health

`GET /healthz` reports process health. `GET /readyz` reports whether the development evaluator is ready. Neither endpoint proves production acceptance.

## Evaluate

Send JSON to `POST /v1/evaluate` containing `request` and `rules`. See `contracts/` and `SPECIFICATIONS.md`.

Do not send secrets, credentials, private keys, raw user content, or unnecessary personal information in policy context.
