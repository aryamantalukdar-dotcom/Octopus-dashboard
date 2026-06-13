#!/usr/bin/env python3
"""Optional local CORS proxy for the Octopus Energy dashboard.

Only needed if your browser blocks direct cross-origin calls to
api.octopus.energy. Run it, then set the dashboard's "API base URL"
(Advanced section on the connect screen) to http://localhost:8001/v1/

Stdlib only — no dependencies. Your API key passes straight through to
Octopus and is never stored or logged.
"""
import http.server
import sys
import urllib.error
import urllib.request

UPSTREAM = "https://api.octopus.energy"
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8001


class Proxy(http.server.BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Authorization, Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self):
        req = urllib.request.Request(UPSTREAM + self.path)
        auth = self.headers.get("Authorization")
        if auth:
            req.add_header("Authorization", auth)
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                body = r.read()
                self.send_response(r.status)
                self._cors()
                self.send_header("Content-Type", r.headers.get("Content-Type", "application/json"))
                self.end_headers()
                self.wfile.write(body)
        except urllib.error.HTTPError as e:
            self.send_response(e.code)
            self._cors()
            self.end_headers()
            self.wfile.write(e.read())
        except Exception:
            self.send_response(502)
            self._cors()
            self.end_headers()

    def log_message(self, fmt, *args):  # keep the terminal quiet
        pass


if __name__ == "__main__":
    print(f"Proxying http://localhost:{PORT} -> {UPSTREAM}")
    print("Set the dashboard's API base URL to "
          f"http://localhost:{PORT}/v1/  (Ctrl-C to stop)")
    http.server.ThreadingHTTPServer(("127.0.0.1", PORT), Proxy).serve_forever()
