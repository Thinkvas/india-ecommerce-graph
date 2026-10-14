"""Local QA server: serves the repo root and accepts POST /dump/<name> -> qa/<name> (used by the browser test harness)."""
import http.server, os, re, sys
ROOT = sys.argv[1]
os.makedirs(os.path.join(ROOT, "qa"), exist_ok=True)
class H(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k): super().__init__(*a, directory=ROOT, **k)
    def do_POST(self):
        m = re.fullmatch(r"/dump/([\w.-]+)", self.path)
        if not m: self.send_error(404); return
        n = int(self.headers.get("Content-Length", 0))
        with open(os.path.join(ROOT, "qa", m.group(1)), "wb") as f: f.write(self.rfile.read(n))
        self.send_response(204); self.end_headers()
http.server.ThreadingHTTPServer(("127.0.0.1", 8766), H).serve_forever()
