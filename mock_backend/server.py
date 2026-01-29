from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = REPO_ROOT / "assets" / "data" / "age_distribution.json"


class MockHandler(BaseHTTPRequestHandler):
    def _send_json(self, payload: dict, status: int = 200) -> None:
        data = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:  # noqa: N802
        if self.path in ("/api/age-distribution", "/api/age-distribution/"):
            if DATA_FILE.exists():
                payload = json.loads(DATA_FILE.read_text(encoding="utf-8"))
                self._send_json(payload)
            else:
                self._send_json(
                    {"error": "age_distribution.json not found"}, status=404
                )
            return

        if self.path == "/":
            self._send_json(
                {
                    "status": "ok",
                    "endpoints": ["/api/age-distribution"],
                }
            )
            return

        self._send_json({"error": "not found"}, status=404)


def main() -> None:
    server = HTTPServer(("0.0.0.0", 8080), MockHandler)
    print("Mock backend running at http://localhost:8080")
    server.serve_forever()


if __name__ == "__main__":
    main()
