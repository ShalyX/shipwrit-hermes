# Shipwrit — outcome-based release proof for Hermes

> Shipped isn't proven. A deployment can succeed while a checkout silently fails.

**Source:** https://github.com/ShalyX/shipwrit-hermes
**Pinned source commit:** `2f3a38e096feefc9041138852417187b793c0af5` (Shipwrit 0.3.2)
**Hosted fixture:** https://shipwrit-demo.vercel.app

## What it adds
- `release_witness_check`: executes bounded, project-owned HTTP user-journey contracts with step assertions and captured values; writes redacted, content-hashed receipts.
- `post_tool_call`: detects recognized deployment attempts in terminal tool metadata and records them as UNVERIFIED.
- `pre_verify`: returns an advisory continuation when a coding turn has a pending deployment without a passing receipt.

A green deploy plus HTTP 200 at checkout but a 404 order lookup becomes **BLOCK**. After repair, the same contract becomes **PASS**. The differentiator is the native Hermes release-completion loop, not a new generic monitoring dashboard. It never patches Hermes core.

## Validation / observed proof
- Current Hermes catalog validator: 15/15 checks, zero warnings, run against the installed 0.3.2 package.
- 21 unit/regression/negative tests passed on the installed 0.3.2 package, including the actual Hermes dispatcher argument context and JSON-text tool result contract.
- Fresh GitHub install/update and enable succeeded in the Caraxes `forge` profile.
- **Actual Hermes LLM session** `20261110_212305_3bbefc` discovered, described and invoked `release_witness_check` twice. Broken GET-only fixture: BLOCK (health 200, order 404), receipt `efecd91785ec00ef37e66be69bc17aa249a7379d24e9de8e17f4009e02f56a5b`. Fixed GET-only fixture: PASS (both 200), receipt `9fc13923072a14b64a5482fdb21c553cda59fb1c8968e2273ce84251996ad9c9`. Both calls used `allow_writes=false`.
- **Live post_tool_call** observed a help-only `vercel deploy --help` terminal command and wrote an UNVERIFIED marker. Vercel CLI was absent; no deployment occurred.
- The loaded Hermes plugin manager reports `pre_verify` registered and returned the expected continuation when directly invoked with a pending marker. An automatic end-of-turn `pre_verify` continuation in a live agent turn is not yet captured; do not claim it was.

## Independent hosted proof
A GitHub Actions runner executed the actual plugin engine against the public Vercel fixture: broken journey BLOCK and corrected journey PASS, with receipts archived:
https://github.com/ShalyX/shipwrit-hermes/actions/runs/42825511858

The hosted app is a controlled seeded fixture. Its fixed mode uses a stateless signed order receipt, **not** a production database.

## Risk disclosure
- **Network:** outbound HTTP(S) requests only to origins explicitly allowlisted in the project contract. Redirects are disabled. No telemetry or third-party service.
- **Filesystem:** reads the project-local JSON contract; writes its own release state and redacted receipts under `.release-witness/`. Does not read .env files or Hermes credential stores.
- **Side effects:** POST/PUT/PATCH/DELETE are permitted only when the caller explicitly passes `allow_writes=true`. They can mutate the target app; use only authorized staging with disposable data and cleanup.
- **Shell/background:** plugin runs no shell commands and starts no background services. Its `post_tool_call` hook observes terminal tool metadata only.
- **Credentials:** no external keys, OAuth clients, or stored credentials.
- **Behavioral boundary:** `pre_verify` is an advisory continuation in coding turns after file edits; it does not block deployment infrastructure.

## Compatibility / limitations
Python standard library only; no third-party runtime dependencies. Uses Hermes standalone plugin interfaces `ctx.register_tool` and `ctx.register_hook`. HTTP/JSON journeys only; no browser or visual assertions. Terminal deployment detection covers recognized commands, not every provider.
