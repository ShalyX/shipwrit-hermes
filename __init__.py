"""Hermes Release Witness plugin: verified release outcomes and optional finish gate."""
from .engine import run_contract
from .guard import record_release_attempt, pre_verify_gate, mark_receipt
SCHEMA={
 "name":"release_witness_check",
 "description":"Verify a deployment with project-owned multi-step HTTP outcome checks and a SHA256 evidence receipt. Use on staging; write steps require explicit allow_writes.",
 "parameters":{
  "type":"object",
  "properties":{
   "base_url":{"type":"string","description":"Target deployment base URL"},
   "contract_path":{"type":"string","default":"release-witness.json"},
   "allow_writes":{"type":"boolean","default":False}
  },
  "required":["base_url"]
 }
}
def handle_check(base_url,contract_path="release-witness.json",allow_writes=False):
    receipt=run_contract(base_url,contract_path=contract_path,allow_writes=allow_writes)
    mark_receipt(receipt,base_url)
    return receipt
def register(ctx):
    ctx.register_tool(name="release_witness_check",toolset="release_witness",
      handler=handle_check,schema=SCHEMA,
      description="Run multi-step deployment outcome contract, preserve evidence and clear pending release on PASS.")
    ctx.register_hook("post_tool_call",record_release_attempt)
    ctx.register_hook("pre_verify",pre_verify_gate)
