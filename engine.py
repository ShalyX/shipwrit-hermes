"""Hermes Release Witness: declarative outcome checks with redacted receipts.
Standard library only. No implicit credentials, redirects, or off-host URLs.
"""
from __future__ import annotations
import hashlib, ipaddress, json, os, re, socket, time
import urllib.error, urllib.parse, urllib.request
from datetime import datetime, timezone
from pathlib import Path

MAX_STEPS = 15
MAX_RESPONSE = 256_000
MAX_TIMEOUT = 15
TEMPLATE = re.compile(r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}")

class ContractError(ValueError):
    pass

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

def _load_contract(root: Path, filename: str):
    if Path(filename).is_absolute():
        raise ContractError("Contract path must be project-relative")
    root = root.resolve()
    file = (root / filename).resolve()
    if file != root and root not in file.parents:
        raise ContractError("Contract escapes the project")
    if not file.is_file() or file.stat().st_size > 64_000:
        raise ContractError("Contract missing or too large")
    data = json.loads(file.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("steps"), list):
        raise ContractError("Contract requires steps array")
    if not 1 <= len(data["steps"]) <= MAX_STEPS:
        raise ContractError("Contract must have 1-15 steps")
    return data

def _validate_url(base_url: str, allowed_hosts: list[str], allow_http: bool):
    u = urllib.parse.urlsplit(base_url)
    if u.scheme not in (["https","http"] if allow_http else ["https"]):
        raise ContractError("HTTPS required unless allow_http configured")
    if not u.hostname or u.username or u.password or u.query or u.fragment:
        raise ContractError("Invalid base URL")
    if u.hostname.lower() not in {str(h).lower() for h in allowed_hosts}:
        raise ContractError("Host not explicitly allowed by project contract")
    return base_url.rstrip("/")

def _resolve(template: str, captures: dict):
    def replace(match):
        key = match.group(1)
        if key not in captures:
            raise ContractError("Missing captured field: " + key)
        val = str(captures[key])
        return urllib.parse.quote(val, safe="")
    return TEMPLATE.sub(replace, template)

def _field(obj, dot_key):
    cur=obj
    for part in dot_key.split("."):
        if not isinstance(cur,dict) or part not in cur:
            return False,None
        cur=cur[part]
    return True,cur

def _http_json(url, method, payload, timeout):
    data=json.dumps(payload).encode() if payload is not None else None
    headers={"Accept":"application/json"}
    if data is not None: headers["Content-Type"]="application/json"
    request=urllib.request.Request(url,data=data,headers=headers,method=method)
    opener=urllib.request.build_opener(urllib.request.ProxyHandler({}),NoRedirect())
    try:
        try:
            resp=opener.open(request,timeout=timeout)
        except urllib.error.HTTPError as exc:
            resp=exc
        with resp:
            status=resp.status
            raw=resp.read(MAX_RESPONSE+1)
            if len(raw)>MAX_RESPONSE:raise ContractError("Response exceeds limit")
            try: body=json.loads(raw)
            except (ValueError,UnicodeDecodeError):body={}
        return status,body
    except (TimeoutError, OSError, urllib.error.URLError) as e:
        raise ContractError(type(e).__name__ + ": " + str(e)[:160]) from e

def run_contract(base_url: str, contract_path: str="release-witness.json",
                 project_dir: str=".", allow_writes: bool=False,
                 write_evidence: bool=True):
    root=Path(project_dir).resolve()
    contract=_load_contract(root,contract_path)
    base=_validate_url(base_url,contract.get("allowed_hosts",[]),bool(contract.get("allow_http",False)))
    timeout=max(1,min(MAX_TIMEOUT,int(contract.get("timeout_s",5))))
    captures={}
    steps=[]
    for index,s in enumerate(contract["steps"]):
        name=str(s.get("name",f"step_{index+1}"))
        method=str(s.get("method","GET")).upper()
        if method not in ("GET","POST","PUT","PATCH","DELETE"):
            raise ContractError("Unsupported HTTP method")
        if method!="GET" and not allow_writes:
            raise ContractError("Write-capable journey requires explicit allow_writes=true")
        path=str(s.get("path",""))
        if not path.startswith("/") or path.startswith("//") or "://" in path:
            raise ContractError("Step path must be site-relative")
        if any(k in path for k in ("#",)): raise ContractError("Fragments disallowed")
        rendered=_resolve(path,captures)
        if ".." in urllib.parse.unquote(rendered).split("/"):
            raise ContractError("Parent path segments disallowed")
        url=base+rendered
        payload=s.get("json")
        if payload is not None and method=="GET":
            raise ContractError("GET cannot have JSON payload")
        try:
            status,body=_http_json(url,method,payload,timeout)
            expect=s.get("expect",{})
            expected_status=int(expect.get("status",200))
            failures=[]
            if status!=expected_status:failures.append("http_status")
            for key,wanted in expect.get("json",{}).items():
                exists,observed=_field(body,key)
                if wanted=="$exists" and not exists:failures.append(key)
                elif wanted=="$nonempty" and (not exists or observed in ("",None,[],{})):failures.append(key)
                elif wanted not in ("$exists","$nonempty") and (not exists or observed!=wanted):failures.append(key)
            if not failures:
                for target,source in s.get("capture",{}).items():
                    ok,val=_field(body,source)
                    if not ok or isinstance(val,(dict,list)):failures.append("capture:"+target)
                    else:captures[target]=val
            body_hash=hashlib.sha256(json.dumps(body,sort_keys=True).encode()).hexdigest()
            steps.append({"name":name,"pass":not failures,"http_status":status,
                          "failed_assertions":failures,"body_sha256":body_hash})
        except ContractError as e:
            steps.append({"name":name,"pass":False,"error":str(e)})
        if not steps[-1]["pass"]:break
    passed=len(steps)==len(contract["steps"]) and all(s["pass"] for s in steps)
    receipt={"contract":contract_path,"target_origin":urllib.parse.urlsplit(base).netloc,
             "timestamp_utc":datetime.now(timezone.utc).isoformat(),
             "verdict":"PASS" if passed else "BLOCK","total_steps":len(contract["steps"]),
             "completed_steps":len(steps),"steps":steps}
    receipt["sha256"]=hashlib.sha256(json.dumps(receipt,sort_keys=True).encode()).hexdigest()
    if write_evidence:
        folder=root/".release-witness"/"runs";folder.mkdir(parents=True,exist_ok=True)
        path=folder/(receipt["timestamp_utc"].replace(":","-").replace("+00:00","Z")+"-"+receipt["sha256"][:10]+".json")
        path.write_text(json.dumps(receipt,indent=2),encoding="utf-8")
        receipt["evidence_path"]=str(path)
    return receipt
