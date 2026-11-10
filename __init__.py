"""Shipwrit: Hermes-native release outcome verification."""
from .engine import run_contract
from .guard import record_release_attempt, pre_verify_gate, mark_receipt

SCHEMA = {
    "name": "release_witness_check",
    "description": (
        "Verify a deployment with project-owned multi-step HTTP outcome checks "
        "and a SHA256 evidence receipt. Use on staging; write steps require "
        "explicit allow_writes."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "base_url": {
                "type": "string",
                "description": "Target deployment base URL",
            },
            "contract_path": {
                "type": "string",
                "default": "release-witness.json",
            },
            "allow_writes": {
                "type": "boolean",
                "default": False,
            },
        },
        "required": ["base_url"],
    },
}


def handle_check(args, **_context):
    """Hermes tool dispatcher passes one argument dictionary plus task context."""
    if not isinstance(args, dict):
        raise TypeError("release_witness_check expects an argument object")

    base_url = args.get("base_url")
    contract_path = args.get("contract_path", "release-witness.json")
    allow_writes = args.get("allow_writes", False)

    if not isinstance(base_url, str) or not base_url.strip():
        raise ValueError("base_url is required")
    if not isinstance(contract_path, str) or not contract_path.strip():
        raise ValueError("contract_path must be a non-empty string")
    if not isinstance(allow_writes, bool):
        raise ValueError("allow_writes must be a boolean")

    receipt = run_contract(
        base_url,
        contract_path=contract_path,
        allow_writes=allow_writes,
    )
    mark_receipt(receipt, base_url)
    return receipt


def register(ctx):
    ctx.register_tool(
        name="release_witness_check",
        toolset="release_witness",
        handler=handle_check,
        schema=SCHEMA,
        description=(
            "Run multi-step deployment outcome contract, preserve evidence "
            "and clear pending release on PASS."
        ),
    )
    ctx.register_hook("post_tool_call", record_release_attempt)
    ctx.register_hook("pre_verify", pre_verify_gate)
