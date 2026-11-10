# Actual Hermes Agent session — 2026-11-10

- Hermes profile: `forge` on Caraxes
- Plugin: Shipwrit 0.3.2
- Model: `gpt-6-luna` via `openai-codex`
- Session: `20261110_212305_3bbefc`
- Target: public controlled fixture `https://shipwrit-demo.vercel.app`
- Tool: `release_witness_check`
- Both calls used `allow_writes=false`; no write request or customer data mutation.

## Tool call 1 — broken contract

- Health: HTTP 200, expected JSON passed.
- Order retrieval: HTTP 404, failed `http_status` and `status` assertions.
- Verdict: **BLOCK**
- Receipt: [live-agent-broken.json](live-agent-broken.json)
- SHA-256: `efecd91785ec00ef37e66be69bc17aa249a7379d24e9de8e17f4009e02f56a5b`

## Tool call 2 — corrected contract

- Health: HTTP 200, expected JSON passed.
- Order retrieval: HTTP 200, confirmed order fields passed.
- Verdict: **PASS**
- Receipt: [live-agent-fixed.json](live-agent-fixed.json)
- SHA-256: `9fc13923072a14b64a5482fdb21c553cda59fb1c8968e2273ce84251996ad9c9`

This is an actual LLM-driven Hermes CLI session invoking the plugin and receiving both receipts. The fixed fixture uses a deterministic stateless signed order receipt; it is not proof of production database persistence.
