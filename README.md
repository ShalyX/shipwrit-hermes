# Shipwrit
### For Hermes Agent · Release proof, not release optimism.

**Your deploy said success. Did the user journey work?**

Shipwrit is a native [Hermes Agent](https://github.com/NousResearch/hermes-agent) plugin that runs a bounded, project-defined HTTP journey after a deployment. It can turn a green deploy into a **BLOCKED** release if a real user outcome—like checkout actually creating a retrievable order—fails. It gives the agent a concrete failed step and saves a content-hashed receipt. After repair, rerun to produce a **PASS** receipt.

> **Shipwrit does not deploy or repair your app by itself.** It verifies an explicitly configured target, reports the outcome, and uses Hermes lifecycle hooks to remind a coding agent not to declare success without proof.

## The moment

| A deployment can look green | Shipwrit proves the outcome |
| --- | --- |
| `vercel deploy --prod` exits 0 | Deployment attempt recorded as `UNVERIFIED` |
| `GET /health` returns 200 | Health check passes |
| `POST /checkout` returns 200 + order ID | Checkout request passes |
| `GET /orders/{order_id}` returns 404 | **BLOCK** — order did not persist |
| Agent fixes the bug and reruns the check | **PASS** — three steps independently observed |
| End-of-turn verification | Passing evidence clears pending release |

The plugin does *not* substitute HTTP status for business truth. Results are deliberately narrow: it only certifies the steps declared in your contract.

## What ships

- **Hermes-native tool:** `release_witness_check` via `ctx.register_tool`, with `base_url`, `contract_path`, and `allow_writes`.
- **Automatic detection:** `post_tool_call` notices recognized deployment commands. It records an unverified deployment attempt.
- **Finish-time proof prompt:** `pre_verify` nudges a coding agent after a detected deployment until the release has a passing receipt. Hermes limits verify nudges; this is **advisory continuation**, not a hard network deployment blocker.
- **Declarative journey:** method/path, expected status, JSON field assertions, field capture, and subsequent lookup through captured values.
- **Safe by default:** origin allowlist, HTTPS unless explicitly permitted, no redirects, bounded response/steps/timeout, project-relative contract files, explicit opt-in for mutating HTTP methods.
- **Redacted evidence:** structured step status and SHA-256 of response bodies, never full response bodies, auth tokens, or request payloads.
- **No vendor API key, database or external monitoring account** required.

## Installation

Prerequisite: a Hermes Agent version supporting standalone Python plugins, `post_tool_call` and `pre_verify` hooks.

```bash
hermes plugins install https://github.com/ShalyX/shipwrit-hermes
hermes plugins enable shipwrit
```

Alternatively place this repository in your `~/.hermes/plugins/shipwrit` directory and enable it. For project-only development, copy to `PROJECT/.hermes/plugins/shipwrit` and set `HERMES_ENABLE_PROJECT_PLUGINS=1`. Restart the Hermes process to load newly enabled plugins.

### Configure one project

Copy [examples/release-witness.json](examples/release-witness.json) to the root of the project you are deploying, rename to `release-witness.json`, and **replace the example's localhost host** with the hostname of your controlled staging environment. Each step is a normal HTTP request with a deterministic expectation.

```json
{
  "guard_deployments": true,
  "allowed_hosts": ["staging.example.com"],
  "timeout_s": 5,
  "steps": [
    {"name": "health", "method": "GET", "path": "/health",
     "expect": {"status": 200, "json": {"status": "ok"}}},
    {"name": "checkout", "method": "POST", "path": "/checkout",
     "json": {"sku": "DEMO-1", "quantity": 1},
     "expect": {"status": 200, "json": {"order_id": "$nonempty"}},
     "capture": {"order_id": "order_id"}},
    {"name": "order_persisted", "method": "GET", "path": "/orders/{order_id}",
     "expect": {"status": 200, "json": {"status": "confirmed"}}}
  ]
}
```

Then ask Hermes:

```text
Run release_witness_check against https://staging.example.com
using our project's release-witness.json. This is the test environment,
and you have my approval to allow_writes for this one test checkout.
Report the failed step and receipt, then fix and rerun if blocked.
```

**Mutating journeys require `allow_writes=true` on the tool call.** Do not aim write-capable checks at a production environment without explicit authorization and test-data cleanup.

## Evidence

The project-local `.release-witness/runs/` directory contains individual JSON receipts. A receipt records timestamp, target hostname, each step's status, failed assertions, response-body SHA-256, and overall `PASS` or `BLOCK`. The final receipt SHA-256 is calculated from the receipt body before the `sha256` and `evidence_path` fields are added.

`PASS` means the configured checks passed at that time; it **does not certify all functionality**, security, storage integrity, or current availability. Hashes support local integrity checks but are not signed independent attestations.

## Development / verification

```bash
python -m unittest discover -s tests -v
hermes plugins validate . --install-deps
```

The second command requires a current Hermes CLI. Older Hermes builds may not expose `plugins validate`; this repository is also tested with the newer catalog validator in an isolated checkout.

## Hosted demonstration

Try the [Shipwrit live fixture](https://shipwrit-demo.vercel.app). It intentionally has two modes: a `200 OK` checkout whose order cannot be retrieved, and a corrected mode whose test order is retrievable. The site is a controlled test fixture and its browser-side preview is **not** a Hermes agent session. The plugin engine's HTTPS integration check is in [tests/staging_check.py](tests/staging_check.py).

## Risk and data-access disclosure

- **Network:** The plugin makes outbound HTTP(S) requests only to hosts explicitly named in the project's `allowed_hosts` contract. It doesn't use a third-party telemetry service. Redirects are disabled. Host allowlisting is a configuration boundary, not a network sandbox.
- **Filesystem:** It reads `release-witness.json` from the current working project directory and writes its own status to `.release-witness/release-state.json` and redacted receipts to `.release-witness/runs/` in that project. It does not read Hermes credential stores or `.env` files.
- **Side effects:** `release_witness_check` can send POST, PUT, PATCH and DELETE requests when **explicitly invoked with `allow_writes=true`**. These requests can mutate the application being tested. Use only an authorized staging app with disposable data and a cleanup plan.
- **Shell / background processes:** The plugin runs no shell commands and spawns no background processes. Its `post_tool_call` hook observes recognized terminal deployment commands to create an unverified-release marker.
- **Credentials / telemetry:** No credentials are stored or transmitted by Shipwrit itself, and no telemetry is collected or uploaded by the plugin. Do not place secrets in project contract JSON files.
- **Control limits:** The finish-time `pre_verify` integration is an agent-continuation suggestion, **not an actual block on Vercel or other deployment infrastructure**, and is only invoked when Hermes reaches the relevant coding verification hook.

## Known limits

- HTTP/JSON contracts only; browser rendering and visual regressions are out of scope for this version.
- Deployment hook detection currently supports recognized terminal commands. It is not a universal integration for every cloud provider or third-party deployment tool.
- `pre_verify` runs only in Hermes coding-context turns that changed files. It nudges rather than forcibly blocking infrastructure deployment.
- Users own staging environments, test data, acceptable writes, and cleanup.
- Initial proof uses an isolated checkout/order demo; a third-party production workload is not claimed.

## Plugin surfaces

| Surface | Name |
| --- | --- |
| Tool | `release_witness_check` |
| Hook | `post_tool_call` |
| Hook | `pre_verify` |
| Hermes core patches | None |
| Runtime Python dependencies | None |

**License:** MIT. Built for the Hermes Agent Plugin Hackathon, 2026.
