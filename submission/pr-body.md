# Shipwrit — outcome-based release proof for Hermes

> Shipped isn't proven. A deployment can succeed while a checkout silently fails.

**Source:** https://github.com/ShalyX/shipwrit-hermes
**Pinned source commit:** `4f2391ebe2e59fd4e987b072f2a8c22aa78f34a4`
**Hosted fixture:** https://shipwrit-demo.vercel.app

## What it adds
- `release_witness_check`: executes bounded, project-owned HTTP user-journey contracts, with step capture and assertions, writes redacted content-hashed outcome receipts.
- `post_tool_call`: records attempted recognized terminal deployments as unverified.
- `pre_verify`: nudges an agent before it claims completion in a coding turn if a detected deployment has no passing receipt.

A green deploy plus HTTP 200 at checkout but a 404 order lookup becomes **BLOCK**. After repairing the app, the same contract becomes **PASS**. Unlike synthetic monitoring dashboards, the differentiating value is its native Hermes release-completion loop. It never patches Hermes core.

## Validation
- Native registration/discovery and lifecycle hook behavior verified on Caraxes in isolated project plugin tests.
- `hermes plugins validate . --install-deps` from the current Hermes main branch: all checks passed, zero warnings.
- 17 unit/regression/negative tests passed, including redirects, host allowlist, mutation opt-in, path traversal, oversized responses, false-green checkout, receipt digest, hook gating.
- Fresh GitHub install via `hermes plugins install ShalyX/shipwrit-hermes --enable` succeeded in isolated Hermes home.
- A public Vercel-hosted seeded fixture is available. External staging proof and a live LLM-driven Hermes turn should only be marked verified when captured separately.

## Risk disclosure (catalog rule 13)
- **Network:** makes outbound HTTP(S) requests to user-allowlisted hosts only; no automatic redirects or telemetry.
- **File reads/writes:** reads a project-local JSON contract; writes redacted receipts and a release status JSON file in that project. No secret store access or .env reading.
- **Side effects:** allows POST/PUT/PATCH/DELETE only when the caller passes `allow_writes=true`. These can mutate the target app; users must use disposable staging data or clean up.
- **Shell/background:** no shell commands executed and no background services created; post-tool hook observes deployment command strings.
- **Credentials:** no external keys, OAuth clients, or stored credentials.
- **Behavioral boundary:** pre_verify is advisory, triggered only in Hermes coding turns reaching the hook; it does not stop deployment infrastructure.

## Compatibility / limitations
Python stdlib, no third-party runtime dependencies. Hermes standalone plugin interfaces `ctx.register_tool` and `ctx.register_hook`. API/JSON journeys only, no browser assertions, and terminal deploy detection doesn't cover every provider.
