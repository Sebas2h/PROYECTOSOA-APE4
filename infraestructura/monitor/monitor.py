"""Monitor HTTP local sin dependencias externas."""
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

SERVICIOS = {
    "nginx": os.getenv("MONITOR_NGINX_URL", "http://127.0.0.1:8090/nginx-ping"),
    "vehiculos_a": os.getenv("MONITOR_JAVA_A_URL", "http://127.0.0.1:8080/actuator/health"),
    "vehiculos_b": os.getenv("MONITOR_JAVA_B_URL", "http://127.0.0.1:8182/actuator/health"),
    "ventas": os.getenv("MONITOR_VENTAS_URL", "http://127.0.0.1:8002/health"),
    "notificaciones": os.getenv("MONITOR_NOTIF_URL", "http://127.0.0.1:8181/actuator/health"),
}


def estado(url):
    try:
        with urlopen(Request(url, headers={"Accept": "application/json"}), timeout=2) as r:
            return {"estado": "UP", "http": r.status}
    except HTTPError as ex:
        return {"estado": "DEGRADED", "http": ex.code}
    except (URLError, TimeoutError, OSError):
        return {"estado": "DOWN", "http": None}


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path not in ("/", "/health"):
            self.send_error(404)
            return
        servicios = {nombre: estado(url) for nombre, url in SERVICIOS.items()}
        cuerpo = json.dumps({"status": "UP", "servicios": servicios}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(cuerpo)))
        self.end_headers()
        self.wfile.write(cuerpo)

    def log_message(self, formato, *args):
        return


if __name__ == "__main__":
    ThreadingHTTPServer(("127.0.0.1", int(os.getenv("MONITOR_PORT", "8083"))), Handler).serve_forever()


