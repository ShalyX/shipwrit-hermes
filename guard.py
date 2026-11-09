"""Optional Hermes-native release proof gate.

The gate is observational until a project explicitly enables
`guard_deployments` in release-witness.json. It NEVER blocks deployment;
it can request another agent turn before unverified success claims.
"""
from __future__ import annotations
import json, os, re
from datetime import datetime, timezone
from pathlib import Path

DEPLOY_RE=re.compile(r"(?:^|[;&|\n]\s*)(?:\S*[/\\])?(?:vercel\s+(?:deploy\b|--prod\b)|netlify\s+deploy\b|wrangler\s+deploy\b|fly(?:ctl)?\s+deploy\b|railway\s+up\b)",re.I)
DEPLOY_TOOLS={"mcp__vercel__createdeployment","mcp__vercel__create_deployment"}
STATE_FILE=".release-witness/release-state.json"

def _root():
    return Path.cwd().resolve()

def _enabled(root):
    f=root/"release-witness.json"
    if not f.is_file() or f.stat().st_size>64000: return False
    try:
        data=json.loads(f.read_text())
        return data.get("guard_deployments") is True
    except (ValueError,OSError): return False

def _load(root):
    p=root/STATE_FILE
    try: return json.loads(p.read_text())
    except (OSError,ValueError): return {}

def _save(root,data):
    p=root/STATE_FILE
    p.parent.mkdir(parents=True,exist_ok=True)
    tmp=p.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(data,indent=2))
    os.replace(tmp,p)

def record_release_attempt(tool_name="",args=None,result=None,session_id="",**kwargs):
    root=_root()
    if not _enabled(root):return None
    name=tool_name.lower()
    if name not in ("terminal","shell_exec","execute_command","terminal_exec") and name not in DEPLOY_TOOLS:
        return None
    command=(args or {}).get("command","") if isinstance(args,dict) else ""
    if name not in DEPLOY_TOOLS and not isinstance(command,str):return None
    if name not in DEPLOY_TOOLS and not DEPLOY_RE.search(command):return None
    data=_load(root)
    data.update({"pending":True,"pending_since":datetime.now(timezone.utc).isoformat(),
                 "deployment_tool":tool_name,"session_id":session_id or "",
                 "status":"UNVERIFIED"})
    _save(root,data)
    return None

def mark_receipt(receipt,base_url):
    root=_root()
    if not _enabled(root):return
    data=_load(root)
    if receipt.get("verdict")=="PASS":
        data.update({"pending":False,"status":"VERIFIED",
                     "verified_at":receipt.get("timestamp_utc"),
                     "receipt_hash":receipt.get("sha256"),
                     "verified_target":base_url})
        _save(root,data)
    elif data.get("pending"):
        data.update({"status":"BLOCKED","last_failed_receipt":receipt.get("sha256")})
        _save(root,data)

def pre_verify_gate(coding=False,attempt=0,changed_paths=None,session_id="",**kwargs):
    root=_root()
    if not _enabled(root) or not coding or attempt>0:return None
    data=_load(root)
    if not data.get("pending"):return None
    if data.get("session_id") and session_id and session_id != data.get("session_id"):
        return None
    return {"action":"continue","message":(
        "Release Witness: a deployment was attempted but the project's outcome contract "
        "has no passing post-deployment receipt. Run release_witness_check against the "
        "deployed target (allow_writes=true only for a safe test environment), inspect "
        "the result, and do not claim release success while verdict is BLOCK. "
        "If verification cannot run, clearly report UNVERIFIED and the blocker."
    )}
