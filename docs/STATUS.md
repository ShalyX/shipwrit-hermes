# Shipwrit — verified execution checkpoint (2026-11-09)

## Product lock
The user explicitly selected Release Witness on 2026-11-09. The externally presented name is **Shipwrit** due to exact-name collision with an earlier “Release Witness” browser QA product. **No product thesis change.**

## Core outcome
A Hermes Agent native plugin verifies user-outcome HTTP journeys with user-defined JSON contracts. A deploy + HTTP 200 can remain BLOCK if checkout does not yield a retrievable order. The agent receives failed-step evidence; a corrected run produces a content-hashed PASS receipt. Two Hermes hooks observe deploy activity and prompt for verification before unsupported release claims.

## Proof registry

| Claim | Status | Evidence |
| --- | --- | --- |
| Clean source / repo | VERIFIED | https://github.com/ShalyX/shipwrit-hermes |
| Native Hermes plugin registration/discovery | VERIFIED on isolated Caraxes | Internal integration scripts and stdout; not independently published |
| Native post_tool_call and pre_verify hook behavior | VERIFIED with injected native events | Internal harness evidence; **not** a real LLM conversation |
| 17 negative/behavioral tests | VERIFIED locally and in GitHub Actions | https://github.com/ShalyX/shipwrit-hermes/actions/runs/42565675025 |
| 15 catalog validator checks, no warnings | VERIFIED locally with current Hermes checkout | No independent public validation receipt yet |
| Fresh GitHub plugin install/enable | VERIFIED in isolated Hermes home | CLI stdout retained in previous operator session |
| Public Vercel fixture deployment | VERIFIED | https://shipwrit-demo.vercel.app |
| Broken fixture BLOCK and corrected fixture PASS through actual engine over HTTPS | VERIFIED on independent GitHub Actions runner | https://github.com/ShalyX/shipwrit-hermes/actions/runs/42565675127 |
| Hosted receipts archived | VERIFIED | GitHub Actions artifact `shipwrit-staging-receipts`, run 42565675127 |
| Live LLM-driven Hermes turn invoking plugin autonomously | UNPROVEN | Must capture real agent session |
| Final 90-second video with actual plugin working | NOT RECORDED | Must capture screen and inspect |
| Catalog PR to NousResearch/hermes-agent | NOT OPEN | Prepared `submission/shipwrit.yaml` and PR body |
| X post and entry form | NOT SUBMITTED | Require live links/receipts |

## Anti-drift / missing P0
- Keep project contract onboarding, native Hermes hooks, test outcomes and receipts as P0.
- A controlled serverless fixture is **not** a third-party production database; never claim so.
- `pre_verify` hook is advisory and runs in coding turns with edits; don't claim infrastructure deployment enforcement.
- The browser preview is **not** a real Hermes session.
- Do not let demo UI work replace native Hermes functionality.

## Next highest-value tasks
1. Reconnect Desktop Commander to reach Caraxes/Windows sessions; preserve active forge gateway.
2. Run a complete live Hermes agent session with Shipwrit enabled in an isolated profile and capture the post_tool_call + pre_verify path.
3. Inspect public UI at 1920x1080 and 390x844; fix visual issues from actual renders.
4. Use GitHub fork to add `plugin-catalog/shipwrit.yaml` in `NousResearch/hermes-agent`, pin tested plugin commit, open and verify catalog PR/CI.
5. Record <90s actual working demo, publish on X tagging @NousResearch, submit official form. No entry is submitted until the receipt is observed.

**Deadline from Nous Research:** Wednesday, November 11, 2026 at 5 PM EST = 11 PM Lagos time. Source https://nousresearch.net/.
