"""Tiny stdlib web demo for ClearDose (demo data only).

Run:  .venv/bin/python demo/server.py
Then open http://localhost:8765/ — a one-page form that calls the
deterministic agent. No photo is stored; uploads are read in memory
and the mock OCR provider reads the selected synthetic sample.
"""
from __future__ import annotations

import html
import json
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cleardose.agent import DeterministicAgent  # noqa: E402
from cleardose.cli import _demo_fetch  # noqa: E402
from cleardose.ocr import MockOCRProvider  # noqa: E402

PAGE = """<!doctype html><html><head><meta charset="utf-8"><title>ClearDose demo</title></head>
<body><h1>ClearDose — demo (DEMO DATA, advisory only)</h1>
<p>Plain-language prescription explanations for older adults. Not medical advice.</p>
<form method="post" action="/explain">
<label>Medicine: <input name="medicine" value="ibuprofen"></label>
<button>Explain</button></form>
<form method="post" action="/flag">
<label>New medicine: <input name="candidate" value="ibuprofen"></label>
<label>Already taking (comma separated): <input name="current" value="warfarin"></label>
<button>Check interactions</button></form>
<form method="post" action="/photo">
<p><strong>Photo — synthetic simulation:</strong> this form does NOT upload
a real photo. It runs the selected synthetic sample label through the
mock OCR provider, so the result is a simulation, not a reading of a
real bottle.</p>
<label>Sample label: <select name="sample"><option>ibuprofen-200mg</option><option>acetaminophen-500mg</option></select></label>
<label>Already taking: <input name="current" value="warfarin"></label>
<button>Read synthetic label photo</button></form>
<pre>{result}</pre></body></html>"""


class Handler(BaseHTTPRequestHandler):
    def _agent(self, sample: str = "ibuprofen-200mg") -> DeterministicAgent:
        return DeterministicAgent(fetch=_demo_fetch, ocr=MockOCRProvider(sample))

    def do_GET(self):  # noqa: N802
        self._send(PAGE.format(result=""))

    def do_POST(self):  # noqa: N802
        length = int(self.headers.get("Content-Length", 0))
        fields = parse_qs(self.rfile.read(length).decode())
        get = lambda k: fields.get(k, [""])[0]  # noqa: E731
        agent = self._agent(get("sample") or "ibuprofen-200mg")
        if self.path == "/explain":
            result = agent.explain(get("medicine"))
        elif self.path == "/flag":
            current = [c.strip() for c in get("current").split(",") if c.strip()]
            result = agent.flag(get("candidate"), current)
        elif self.path == "/photo":
            current = [c.strip() for c in get("current").split(",") if c.strip()]
            result = agent.photo(b"synthetic-demo-bytes", current)
        else:
            result = {"error": "unknown path"}
        self._send(PAGE.format(result=html.escape(json.dumps(result, indent=2))))

    def _send(self, body: str) -> None:
        data = body.encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *args):  # keep demo output quiet
        pass


if __name__ == "__main__":
    print("ClearDose demo at http://127.0.0.1:8765/")
    HTTPServer(("127.0.0.1", 8765), Handler).serve_forever()
