#!/usr/bin/env python3
"""Verify a Shipwrit receipt's self-contained SHA-256 integrity hash."""
import argparse
import hashlib
import json
from pathlib import Path

def verify(path: Path) -> tuple[bool,str,str]:
    doc=json.loads(path.read_text(encoding="utf8"))
    reported=doc.get("sha256","")
    payload={k:v for k,v in doc.items() if k not in ("sha256","evidence_path")}
    actual=hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest()
    return bool(reported and reported==actual),reported,actual

if __name__=="__main__":
    parser=argparse.ArgumentParser(description="Verify a Shipwrit evidence receipt; no network calls")
    parser.add_argument("receipt",type=Path)
    args=parser.parse_args()
    ok,expected,actual=verify(args.receipt)
    print("VALID receipt digest" if ok else "INVALID receipt digest")
    print("observed:",actual)
    print("recorded:",expected or "<missing>")
    raise SystemExit(0 if ok else 1)
