"""Public Vercel fixture smoke test using the actual Shipwrit engine.

This is a seeded demonstration of broken/fixed behavior. It is not a claim
that a third-party customer's production database was verified.
"""
import hashlib
import json
import os
import sys
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from engine import run_contract

target = os.environ.get("SHIPWRIT_STAGING_URL", "https://shipwrit-demo.vercel.app").rstrip("/")
host = urlsplit(target).hostname
assert target.startswith("https://") and host, "Staging must use HTTPS"
out = ROOT / "staging-evidence"
out.mkdir(parents=True, exist_ok=True)
results = {}

for mode in ("broken", "fixed"):
    contract = {
        "name": "shipwrit-public-fixture-" + mode,
        "guard_deployments": False,
        "allowed_hosts": [host],
        "timeout_s": 12,
        "steps": [
            {"name": "health", "method": "GET", "path": "/api/health?mode=" + mode,
             "expect": {"status": 200, "json": {"status": "ok", "release": mode}}},
            {"name": "checkout", "method": "POST", "path": "/api/checkout?mode=" + mode,
             "json": {"sku": "SKU-1", "quantity": 1},
             "expect": {"status": 200, "json": {"accepted": True, "order_id": "$nonempty"}},
             "capture": {"order_id": "order_id"}},
            {"name": "order_retrievable", "method": "GET",
             "path": "/api/orders?order_id={order_id}&mode=" + mode,
             "expect": {"status": 200, "json": {"status": "confirmed", "sku": "SKU-1", "quantity": 1}}}
        ]
    }
    path = out / ("contract-" + mode + ".json")
    path.write_text(json.dumps(contract, indent=2), encoding="utf-8")
    receipt = run_contract(target, contract_path=path.name,
                           project_dir=str(out), allow_writes=True)
    expected = "BLOCK" if mode == "broken" else "PASS"
    assert receipt["verdict"] == expected, json.dumps(receipt, indent=2)
    assert receipt["steps"][0]["pass"] is True
    assert receipt["steps"][1]["pass"] is True
    assert receipt["steps"][2]["pass"] is (mode == "fixed")
    stored = json.loads(Path(receipt["evidence_path"]).read_text(encoding="utf-8"))
    body = {k: v for k, v in stored.items() if k not in ("sha256", "evidence_path")}
    assert hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest() == stored["sha256"]
    results[mode] = {
        "verdict": receipt["verdict"],
        "step_status": [{"name": s["name"], "pass": s["pass"],
                         "http_status": s["http_status"]} for s in receipt["steps"]],
        "receipt_sha256": receipt["sha256"],
    }

summary = {
    "environment": "Public HTTPS Vercel-hosted seeded fixture (not a third-party production application)",
    "target": target,
    "behavioral_claim": "A false-green checkout fails; a corrected, retrievable demo order passes",
    "results": results
}
(out / "staging-verification.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
print(json.dumps(summary, indent=2))
print("STAGING_PROOF_VERIFIED")
