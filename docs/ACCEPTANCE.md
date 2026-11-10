# Shipwrit acceptance and reproduction

## Locked promise
Hermes verifies deployed business outcomes before claiming release success. A green deploy plus a 200 checkout that did not yield a retrievable order must be reported as BLOCK.

## Reproducible hosted fixture
The [hosted fixture](https://shipwrit-demo.vercel.app) serves two **deliberately seeded** variants. It is not a customer production service, and its fixed variant uses a stateless receipt rather than database persistence.

```bash
python -m unittest discover -s tests -v
python tests/staging_check.py
```

The second command makes actual HTTPS requests to Vercel. It first calls health, then submits a disposable fixture checkout, captures the returned order ID, and checks retrieval. The broken variant must yield **BLOCK** with the final step failing; the fixed variant must yield **PASS** with all three steps passing. It writes hash-verified receipts under `staging-evidence/`; GitHub Actions archives them.

## Actual Hermes LLM proof (2026-11-10)
The public GitHub package was installed and enabled in Caraxes' `forge` profile. In actual Hermes CLI session `20261110_212305_3bbefc`, model `gpt-6-luna` discovered the plugin tool and invoked `release_witness_check` twice over HTTPS:
- Broken GET-only contract: **BLOCK**, health HTTP 200, order lookup HTTP 404. Receipt SHA-256: `efecd91785ec00ef37e66be69bc17aa249a7379d24e9de8e17f4009e02f56a5b`.
- Fixed GET-only contract: **PASS**, health and order lookup HTTP 200. Receipt SHA-256: `9fc13923072a14b64a5482fdb21c553cda59fb1c8968e2273ce84251996ad9c9`.

Both calls used `allow_writes=false`. The actual handler accepts Hermes' argument-dictionary plus task-context dispatch and returns JSON text, as required by the registry.

## Native lifecycle hooks
The actual `post_tool_call` hook observed a help-only `vercel deploy --help` terminal command and persisted `UNVERIFIED` release state. Vercel CLI was absent, so no deployment occurred. The active Hermes plugin manager also confirmed `pre_verify` registration and returned its expected continuation when invoked with a pending marker, `coding=true`, and `attempt=0`. The automatic end-of-turn continuation was not captured in a real agent turn; do not claim it was.

## Protection and limitations
- Staging target must be explicitly allowlisted, HTTPS by default.
- Mutating requests require `allow_writes=true`; use only test data and authorized targets.
- No redirects, response bodies, telemetry, or background process.
- `pre_verify` is advisory; it is **not** a hard gate preventing Vercel or another provider from deploying.
- The hosted fixed fixture is stateless; it is not production database proof.
