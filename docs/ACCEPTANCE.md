# Shipwrit acceptance and reproduction

## Locked promise
Hermes verifies deployed business outcomes before claiming release success. A green deploy plus a 200 checkout that did not yield a retrievable order must be reported as BLOCK.

## Reproducible hosted fixture
The [hosted fixture](https://shipwrit-demo.vercel.app) serves two **deliberately seeded** variants. It is not a customer production service, and its fixed variant uses a stateless receipt rather than database persistence.

```bash
python -m unittest discover -s tests -v
python tests/staging_check.py
```

The second command makes actual HTTPS requests to Vercel. It first calls health, then submits a disposable checkout, captures the returned order ID, and checks retrieval. The broken variant must yield **BLOCK** with the final step failing; the fixed variant must yield **PASS** with all three steps passing. The script writes hash-verified receipts under `staging-evidence/` and fails the process on any mismatch. The GitHub Actions *Hosted journey proof* workflow archives these artifacts.

## Hermes-native proof
A fresh install from `ShalyX/shipwrit-hermes` in a separate Hermes home succeeded on Caraxes. The package's actual `register(ctx)` entrypoint adds a tool and the `post_tool_call`/`pre_verify` hooks. Native registry and injected hook-event test assertions passed in the isolated harness; those are **not** evidence of a live LLM's autonomous behavior.

## Protection and limitations
- Staging target must be explicitly allowlisted, HTTPS by default.
- Mutating requests require `allow_writes=true`; use only test data and authorized target.
- No redirects, response bodies logged, external telemetry, or background process.
- Pre-verify requests evidence in the Hermes coding loop; it is **not** a hard gate preventing Vercel from deploying.
- Live model session, visual QA, demo recording, catalog PR, and entry form must be independently verified before claiming submission completion.
