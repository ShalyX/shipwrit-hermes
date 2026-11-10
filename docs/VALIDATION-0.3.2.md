# Shipwrit 0.3.2 validation record — 2026-11-10

## Hermes catalog validator
The current Hermes main-branch catalog validator ran against the installed 0.3.2 package and returned `ok: true`, **15/15 checks**, zero warnings:
- manifest and required fields
- Hermes compatibility declaration
- config and environment declarations
- OAuth declaration
- loadable entrypoint
- Python dependencies
- isolated capability registration probe
- declared tools, hooks and middleware
- built-in tool collision scan
- security scan
- no Hermes core override

The validator was run from a fresh/current checkout of `NousResearch/hermes-agent` against the actual Caraxes forge-profile installation.

## Hermes integration
Actual Hermes CLI session `20261110_212305_3bbefc` invoked the plugin twice and received serialized JSON receipts:
- Broken fixture BLOCK, health 200, order lookup 404: `efecd91785ec00ef37e66be69bc17aa249a7379d24e9de8e17f4009e02f56a5b`.
- Fixed fixture PASS, health and order lookup 200: `9fc13923072a14b64a5482fdb21c553cda59fb1c8968e2273ce84251996ad9c9`.
Both calls were GET-only and used `allow_writes=false`.

A live `post_tool_call` probe recorded a help-only deployment command as UNVERIFIED. No deployment occurred. The active plugin manager also confirmed `pre_verify` registration and callback behavior; automatic turn-end firing in a live agent session remains unproven.

## Regression suite
21 tests passed on the installed 0.3.2 plugin. The suite includes the Hermes dispatch signature, task context, JSON-text result contract, HTTP fixture behavior, receipt digest, host allowlist, redirects, mutation opt-in, and deployment guard behavior.
