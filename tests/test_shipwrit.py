"""Black-box contract, guard, and receipt tests; no external network."""
from __future__ import annotations
import hashlib, json, os, tempfile, unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread

import engine
import guard

class Fixture(BaseHTTPRequestHandler):
    broken = True
    orders = {}
    def log_message(self,*args):pass
    def send(self,status,body,location=None):
        raw=json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type","application/json")
        if location:self.send_header("Location",location)
        self.send_header("Content-Length",str(len(raw)))
        self.end_headers();self.wfile.write(raw)
    def do_GET(self):
        if self.path=="/health":return self.send(200,{"status":"ok","secret":"do-not-leak"})
        if self.path=="/redirect":return self.send(302,{"redirect":True},"http://example.com/")
        if self.path=="/oversize":return self.send(200,{"huge":"x"*300000})
        if self.path.startswith("/orders/"):
            order=self.orders.get(self.path.split("/")[-1])
            return self.send(200 if order else 404,order or {"error":"missing"})
        return self.send(404,{"error":"not_found"})
    def do_POST(self):
        size=int(self.headers.get("Content-Length","0"))
        body=json.loads(self.rfile.read(size))
        if self.path!="/checkout":return self.send(404,{"error":"not_found"})
        if body!={"sku":"SKU-1","quantity":1}:return self.send(422,{"error":"bad_input"})
        if not Fixture.broken:
            Fixture.orders["order-99"]={"status":"confirmed","sku":"SKU-1","quantity":1}
        return self.send(200,{"accepted":True,"order_id":"order-99","access_token":"do-not-leak"})

def contract(extra=None):
    c={"name":"checkout-persistence","guard_deployments":True,
       "allowed_hosts":["127.0.0.1"],"allow_http":True,"timeout_s":3,
       "steps":[
          {"name":"health","path":"/health","expect":{"status":200,"json":{"status":"ok"}}},
          {"name":"checkout","method":"POST","path":"/checkout","json":{"sku":"SKU-1","quantity":1},
           "expect":{"status":200,"json":{"accepted":True,"order_id":"$nonempty"}},
           "capture":{"order_id":"order_id"}},
          {"name":"order_persisted","path":"/orders/{order_id}",
           "expect":{"status":200,"json":{"status":"confirmed","sku":"SKU-1"}}}
       ]}
    if extra:c.update(extra)
    return c

class EngineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server=ThreadingHTTPServer(("127.0.0.1",0),Fixture)
        cls.thread=Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start()
        cls.url=f"http://127.0.0.1:{cls.server.server_port}"
    @classmethod
    def tearDownClass(cls):cls.server.shutdown();cls.server.server_close()
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        (self.root/"release-witness.json").write_text(json.dumps(contract()))
        Fixture.broken=True;Fixture.orders={}
    def runcheck(self,**kwargs):
        return engine.run_contract(self.url,project_dir=str(self.root),allow_writes=True,**kwargs)
    def test_false_green_checkout_blocked(self):
        r=self.runcheck();self.assertEqual(r["verdict"],"BLOCK")
        self.assertEqual(r["completed_steps"],3)
        self.assertEqual(r["steps"][-1]["name"],"order_persisted")
        self.assertEqual(r["steps"][-1]["failed_assertions"],["http_status","status","sku"])
    def test_repaired_checkout_passes(self):
        Fixture.broken=False
        r=self.runcheck();self.assertEqual(r["verdict"],"PASS")
        self.assertTrue(all(x["pass"] for x in r["steps"]))
        self.assertTrue(Path(r["evidence_path"]).exists())
    def test_receipt_redacts_payload_and_secrets(self):
        r=self.runcheck()
        data=Path(r["evidence_path"]).read_text()
        self.assertNotIn("do-not-leak",data)
        self.assertNotIn("access_token",data)
        self.assertIn("body_sha256",data)
    def test_mutating_journey_requires_optin(self):
        with self.assertRaises(engine.ContractError):
            engine.run_contract(self.url,project_dir=str(self.root))
    def test_unallowlisted_hostname(self):
        with self.assertRaises(engine.ContractError):
            engine.run_contract(self.url.replace("127.0.0.1","localhost"),project_dir=str(self.root),allow_writes=True)
    def test_https_default(self):
        (self.root/"release-witness.json").write_text(json.dumps(contract({"allow_http":False})))
        with self.assertRaises(engine.ContractError):self.runcheck()
    def test_contract_path_traversal(self):
        with self.assertRaises(engine.ContractError):
            self.runcheck(contract_path="../release-witness.json")
    def test_invalid_step_path(self):
        c=contract();c["steps"]=[{"path":"//evil.com"}]
        (self.root/"release-witness.json").write_text(json.dumps(c))
        with self.assertRaises(engine.ContractError):self.runcheck()
    def test_redirect_not_followed(self):
        c=contract();c["steps"]=[{"name":"redirect","path":"/redirect","expect":{"status":200}}]
        (self.root/"release-witness.json").write_text(json.dumps(c))
        r=self.runcheck();self.assertEqual(r["verdict"],"BLOCK")
        self.assertEqual(r["steps"][0]["http_status"],302)
    def test_oversized_response_blocked(self):
        c=contract();c["steps"]=[{"name":"oversize","path":"/oversize","expect":{"status":200}}]
        (self.root/"release-witness.json").write_text(json.dumps(c))
        r=self.runcheck();self.assertEqual(r["verdict"],"BLOCK")
        self.assertIn("limit",r["steps"][0]["error"])
    def test_too_many_steps(self):
        c=contract();c["steps"]=[{"path":"/health"}]*16
        (self.root/"release-witness.json").write_text(json.dumps(c))
        with self.assertRaises(engine.ContractError):self.runcheck()
    def test_receipt_digest_matches(self):
        r=self.runcheck()
        expected=r["sha256"]
        payload={k:v for k,v in r.items() if k not in ("sha256","evidence_path")}
        actual=hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest()
        self.assertEqual(actual,expected)

class GuardTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.original=Path.cwd();os.chdir(self.tmp.name)
        self.addCleanup(os.chdir,self.original)
        Path("release-witness.json").write_text(json.dumps(contract()))
    def test_ignored_unrelated_command(self):
        guard.record_release_attempt(tool_name="terminal",args={"command":"npm run build"},session_id="session")
        self.assertFalse(Path(guard.STATE_FILE).exists())
    def test_detect_deploy_and_nudge(self):
        guard.record_release_attempt(tool_name="terminal",args={"command":"vercel deploy --prod"},session_id="session")
        state=json.loads(Path(guard.STATE_FILE).read_text())
        self.assertTrue(state["pending"])
        self.assertIn("Release Witness",guard.pre_verify_gate(coding=True,attempt=0,session_id="session")["message"])
        self.assertIsNone(guard.pre_verify_gate(coding=False,attempt=0,session_id="session"))
        self.assertIsNone(guard.pre_verify_gate(coding=True,attempt=1,session_id="session"))
        self.assertIsNone(guard.pre_verify_gate(coding=True,attempt=0,session_id="other"))
    def test_receipt_block_keeps_pending(self):
        guard.record_release_attempt(tool_name="terminal",args={"command":"vercel deploy --prod"},session_id="session")
        guard.mark_receipt({"verdict":"BLOCK","sha256":"bad"},"https://staging.example.com")
        self.assertTrue(json.loads(Path(guard.STATE_FILE).read_text())["pending"])
    def test_receipt_pass_clears_pending(self):
        guard.record_release_attempt(tool_name="terminal",args={"command":"vercel deploy --prod"},session_id="session")
        guard.mark_receipt({"verdict":"PASS","sha256":"good","timestamp_utc":"2026-11-09T00:00:00Z"},"https://staging.example.com")
        self.assertFalse(json.loads(Path(guard.STATE_FILE).read_text())["pending"])
        self.assertIsNone(guard.pre_verify_gate(coding=True,attempt=0,session_id="session"))
    def test_optin_required(self):
        Path("release-witness.json").write_text(json.dumps(contract({"guard_deployments":False})))
        guard.record_release_attempt(tool_name="terminal",args={"command":"vercel deploy --prod"},session_id="session")
        self.assertFalse(Path(guard.STATE_FILE).exists())

if __name__=="__main__":unittest.main()
