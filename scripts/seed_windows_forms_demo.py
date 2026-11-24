"""Crea datos reales para demostrar los listados de Windows Forms."""
import json
import time
from pathlib import Path
from urllib import parse, request, error


root = Path(__file__).resolve().parents[1]
environment = json.loads(
    (root / ".runtime" / "APE04_LOCAL_QA_PRIVADO.postman_environment.json")
    .read_text(encoding="utf-8")
)
values = {item["key"]: item.get("value", "") for item in environment["values"]}
base_url = values["baseUrl"].rstrip("/")


def call(method, route, token=None, payload=None, extra_headers=None):
    headers = dict(extra_headers or {})
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = None
    if payload is not None:
        data = json.dumps(payload).encode()
        headers["Content-Type"] = "application/json"
    req = request.Request(base_url + route, data=data, headers=headers, method=method)
    try:
        with request.urlopen(req, timeout=15) as response:
            body = response.read()
            return response.status, json.loads(body) if body else None
    except error.HTTPError as exc:
        body = exc.read().decode(errors="replace")
        raise RuntimeError(f"{method} {route} devolvió HTTP {exc.code}: {body[:300]}") from exc


form = parse.urlencode({
    "grant_type": "password",
    "username": values["operadorUser"],
    "password": values["operadorPassword"],
}).encode()
login = request.Request(
    base_url + "/oauth/token",
    data=form,
    headers={
        "Authorization": f"Basic {values['oauthBasic']}",
        "Content-Type": "application/x-www-form-urlencoded",
    },
    method="POST",
)
with request.urlopen(login, timeout=15) as response:
    token = json.loads(response.read())["access_token"]

_, compradores = call("GET", "/api/compradores", token)
if not compradores:
    raise RuntimeError("No existe un comprador visible para el usuario operador.")
comprador = max(compradores, key=lambda item: item["id"])

stamp = str(int(time.time()))[-7:]
vehiculos = []
for index in range(1, 7):
    marker = f"{stamp}{index}"
    _, vehiculo = call("POST", "/api/vehiculos", token, {
        "marca": ["Toyota", "Chevrolet", "Kia", "Hyundai", "Mazda", "Nissan"][index - 1],
        "modelo": f"APE04 Demo {index}",
        "placa": f"D{marker[-6:]}",
        "chasis": f"DM{marker[-8:]}ABCDEFG",
        "anio": 2026,
        "color": ["Azul", "Rojo", "Negro", "Blanco", "Gris", "Verde"][index - 1],
        "precio": 22000 + index * 750,
    })
    vehiculos.append(vehiculo["idVehiculo"])

ventas = []
for index, vehiculo_id in enumerate(vehiculos[:3], start=1):
    _, venta = call(
        "POST", "/api/ventas", token,
        {"vehiculoId": vehiculo_id, "compradorId": comprador["id"]},
        {"Idempotency-Key": f"wf-demo-{stamp}-{index}"},
    )
    ventas.append(venta["id"])

print(json.dumps({
    "compradorId": comprador["id"],
    "vehiculosCreados": vehiculos,
    "ventasRegistradas": ventas,
    "vehiculosDisponiblesRestantes": vehiculos[3:],
}, ensure_ascii=False))
