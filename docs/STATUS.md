# Shipwrit — verified execution checkpoint (2026-11-10)

## Product lock
The user explicitly selected Release Witness on 2026-11-09. The public brand is **Shipwrit** after an exact-name collision check. This is a name change only; the approved product thesis remains unchanged.

## Core outcome
A Hermes Agent native plugin verifies project-defined user-outcome HTTP journeys. A deployment command and HTTP 200 checkout response are insufficient if the returned order cannot be retrieved. Shipwrit returns a failed-step diagnosis and redacted SHA-256 receipt; a corrected run produces PASS.

## Proof registry

| Claim | Status | Evidence |
|---|---|---|
| Public source repository | VERIFIED | https://github.com/ShalyX/shipwrit-hermes |
| Plugin version | 0.3.2 | Exact source pin: `12cb58dadb27a3963510ad681bee62aaa5d970c9` |
| Fresh GitHub install and enable | VERIFIED | Installed to Caraxes active `forge` profile; CLI discovers plugin. Gateway not restarted. |
| Hermes plugin discovery and tool registration | VERIFIED | Real Hermes CLI session enabled `release_witness`, discovered `release_witness_check`, described it and invoked it. |
| Actual LLM-driven Hermes tool execution | VERIFIED | Session `20261110_212305_3bbefc`, model `gpt-6-luna` via `openai-codex`. Two actual tool calls returned usable JSON-text receipts. |
| Broken fixture outcome | VERIFIED | BLOCK. Health HTTP 200; order retrieval HTTP 404. Receipt SHA256: `efecd91785ec00ef37e66be69bc17aa249a7379d24e9de8e17f4009e02f56a5b`. |
| Corrected fixture outcome | VERIFIED | PASS. Health and order retrieval both HTTP 200. Receipt SHA256: `9fc13923072a14b64a5482fdb21c553cda59fb1c8968e2273ce84251996ad9c9`. |
| Live post_tool_call detection | VERIFIED | Session `20261110_212507_c0ffa9`; harmless `vercel deploy --help` probe created `.release-witness/release-state.json` with `pending=true`, `status=UNVERIFIED`. Vercel CLI was not installed, so no deployment occurred. |
| pre_verify registration and callback behavior | VERIFIED AT PLUGIN-MANAGER LEVEL | Active forge plugin manager reports both hooks registered; calling pre_verify with coding=true, attempt=0 and a pending release returns the expected continuation. |
| Automatic pre_verify turn-end firing in a live agent turn | NOT YET VERIFIED | The live CLI probe did not emit a continuation; likely no tracked changed-path condition was present. Do not claim full live pre_verify proof. |
| Unit / regression / security-negative tests | 21/21 PASS on installed 0.3.2 | Caraxes installed plugin test suite. Includes real dispatcher argument context and JSON-text result contract. |
| Current Hermes catalog validator | 15/15 PASS on earlier 0.3.0 package | Re-run against 0.3.2 before upstream PR final review. |
| Public Vercel fixture | VERIFIED | https://shipwrit-demo.vercel.app |
| Independent CI staging test | VERIFIED | https://github.com/ShalyX/shipwrit-hermes/actions/runs/42565675127 — controlled fixture BLOCK then PASS, receipts archived. |
| Final judge-facing video | NOT RECORDED | Need actual Hermes CLI run + receipt sequence, <90 seconds. |
| Upstream catalog PR | IN PROGRESS | Fork created: https://github.com/ShalyX/hermes-agent. Add pinned entry and open PR to NousResearch/hermes-agent. |
| X post / official entry form | NOT SUBMITTED | Submit only after upstream PR link and final demo link are available. |

## Explicit limitations / anti-drift
- The hosted Vercel fixture is a controlled seeded, stateless demonstration, **not** a customer production database.
- Live Hermes proof used GET-only contracts with `allow_writes=false`; no customer data was changed.
- The post_tool_call test observed a help-only command, not a real deployment.
- `pre_verify` is an advisory continuation, only called in coding turns after file edits. It is not a deployment infrastructure block.
- The global forge profile has Shipwrit enabled, but the already-running messaging gateway has not been restarted. New CLI sessions load the plugin; do not claim gateway activation until restart.
- The current auxiliary title-generation model returns HTTP 410 (retired NVIDIA model). This did not block agent turns or Shipwrit tool execution; it is unrelated to product proof.
- Do not broaden into generic monitoring, browser automation or a dashboard before the P0 submission path is complete.

## Next critical tasks
1. Catalog validation for 0.3.2 is complete (15/15, zero warnings).
2. Add `plugin-catalog/shipwrit.yaml` to the ShalyX fork, pinned to `12cb58dadb27a3963510ad681bee62aaa5d970c9`, and open upstream PR.
3. Confirm upstream PR CI and review the exact diff.
4. Capture the actual live Hermes CLI session (broken BLOCK → corrected PASS) and receipts in a <90-second screen recording. No fake logs or implied production database.
5. Inspect the hosted landing page at desktop/mobile sizes; make only judge-impacting fixes.
6. Publish X post tagging @NousResearch and submit official form. Verify the entry receipt before claiming submission.

**Deadline:** Wednesday, November 11, 2026 at 5 PM EST (11 PM Lagos time). Source: https://nousresearch.net/.
