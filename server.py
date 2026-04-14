#!/usr/bin/env python3
"""
Servidor HTTP para Memorama Arcade Retro.
Sirve archivos estáticos y expone una API REST para el leaderboard compartido.

Uso:
    python server.py
    PORT=9000 python server.py
"""

import http.server
import json
import os
import socket
import sys

SCORES_FILE = "scores.json"
PORT = int(os.environ.get("PORT", 8080))

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, DELETE, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
}


def _read_scores():
    """Lee scores.json del disco. Retorna [] si no existe o está corrupto."""
    try:
        with open(SCORES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            return []
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return []


def _write_scores(entries):
    """Escribe entries en scores.json."""
    with open(SCORES_FILE, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)


class ScoresHandler(http.server.SimpleHTTPRequestHandler):

    def _send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        for k, v in CORS_HEADERS.items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        if self.path == "/api/scores":
            self.send_response(200)
            for k, v in CORS_HEADERS.items():
                self.send_header(k, v)
            self.end_headers()
        else:
            super().do_OPTIONS() if hasattr(super(), "do_OPTIONS") else self.send_error(405)

    def do_GET(self):
        if self.path == "/api/scores":
            self._send_json(_read_scores())
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == "/api/scores":
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length)
            try:
                entries = json.loads(raw)
                if not isinstance(entries, list):
                    entries = []
            except (json.JSONDecodeError, ValueError):
                entries = []
            _write_scores(entries)
            self._send_json({"ok": True})
        else:
            self.send_error(404)

    def do_DELETE(self):
        if self.path == "/api/scores":
            _write_scores([])
            self._send_json({"ok": True})
        else:
            self.send_error(404)

    def log_message(self, fmt, *args):
        # Silenciar logs de acceso para mantener la salida limpia
        pass


def get_local_ip():
    """Obtiene la IP local de la máquina en la red."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except OSError:
        return "localhost"


def main():
    local_ip = get_local_ip()
    url = f"http://{local_ip}:{PORT}/index.html"

    print()
    print("  ==========================================")
    print("   MEMORAMA ARCADE RETRO — Servidor Local")
    print("  ==========================================")
    print(f"   IP local  : {local_ip}")
    print(f"   URL red   : {url}")
    print(f"   localhost : http://localhost:{PORT}/index.html")
    print()
    print("   Comparte la URL de red con otros dispositivos")
    print("   Presiona Ctrl+C para detener el servidor")
    print("  ==========================================")
    print()

    server = http.server.HTTPServer(("", PORT), ScoresHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Servidor detenido.")
        sys.exit(0)


if __name__ == "__main__":
    main()
