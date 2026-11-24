import base64
import json
import secrets
import time
from pathlib import Path

import bcrypt
import pymysql
from urllib import parse, request

root = Path(__file__).resolve().parents[1]
runtime = root / ".runtime"
runtime.mkdir(exist_ok=True)

local_secrets = {}
secrets_file = runtime / "secrets.env"
for line in secrets_file.read_text(encoding="utf-8-sig").splitlines():
    if "=" in line and not line.lstrip().startswith("#"):
        key, value = line.split("=", 1)
        local_secrets[key] = value

accounts = {
    "qa-operador": ("OPERADOR", secrets.token_urlsafe(24)),
    "qa-consulta": ("CONSULTA", secrets.token_urlsafe(24)),
    "qa-admin": ("ADMIN", secrets.token_urlsafe(24)),
}

db = pymysql.connect(host="127.0.0.1", user="root", password="", database="venta_vehiculos", autocommit=True)
with db.cursor() as cur:
    for username, (role, password) in accounts.items():
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        cur.execute(
            "INSERT INTO usuarios_api(username,password,rol) VALUES(%s,%s,%s) "
            "ON DUPLICATE KEY UPDATE password=VALUES(password), rol=VALUES(rol)",
            (username, hashed, role),
        )
db.close()

client_id = local_secrets["OAUTH_CLIENT_ID"]
client_secret = local_secrets["OAUTH_CLIENT_SECRET"]
oauth_basic = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()

source = root / "postman" / "APE04_LOCAL_SANITIZADO.postman_environment.json"
environment = json.loads(source.read_text(encoding="utf-8"))
values = {item["key"]: item for item in environment["values"]}
values["oauthBasic"]["value"] = oauth_basic
values["operadorUser"]["value"] = "qa-operador"
values["operadorPassword"]["value"] = accounts["qa-operador"][1]
values["consultaUser"]["value"] = "qa-consulta"
values["consultaPassword"]["value"] = accounts["qa-consulta"][1]
suffix = str(int(time.time()))[-8:]
values["qaSuffix"]["value"] = suffix
values["qaPlate"]["value"] = f"Q{suffix[-6:]}"
values["qaChassis"]["value"] = f"QA{suffix}ABCDEFG"
values["qaDocument"]["value"] = f"DOC{suffix}"
values["qaEmail"]["value"] = f"qa{suffix}@example.test"

base_url = values["baseUrl"]["value"]
token_req = request.Request(
    f"{base_url}/oauth/token",
    data=parse.urlencode({"grant_type": "password", "username": "qa-operador", "password": accounts["qa-operador"][1]}).encode(),
    headers={"Authorization": f"Basic {oauth_basic}", "Content-Type": "application/x-www-form-urlencoded"},
    method="POST",
)
token = json.loads(request.urlopen(token_req, timeout=10).read())["access_token"]
headers = {"Authorization": f"Bearer {token}"}

def post_json(url, payload):
    req = request.Request(url, data=json.dumps(payload).encode(), headers={**headers, "Content-Type": "application/json"}, method="POST")
    return json.loads(request.urlopen(req, timeout=10).read())

def create_vehicle(index):
    marker = f"{suffix}{index}"
    payload = {
        "marca": "APE04",
        "modelo": f"Preparado {index}",
        "placa": f"S{marker[-6:]}",
        "chasis": f"QB{marker[-8:]}ABCDEFG",
        "anio": 2026,
        "color": "Azul",
        "precio": 21000 + index,
    }
    return post_json(f"{base_url}/api/vehiculos", payload)["idVehiculo"]

values["vehiculoId"]["value"] = str(create_vehicle(1))
values["vehiculoIdAlt"]["value"] = str(create_vehicle(2))
buyer = post_json(f"{base_url}/api/compradores", {"documento": f"SEED{suffix}", "nombre": "Comprador preparado", "correo": f"seed{suffix}@example.test"})
values["compradorId"]["value"] = str(buyer["id"])
values["idempotencyKey"]["value"] = f"ape04-{suffix}-idempotencia"
environment["name"] = "APE04 Local QA Privado"
(runtime / "APE04_LOCAL_QA_PRIVADO.postman_environment.json").write_text(
    json.dumps(environment, indent=2), encoding="utf-8"
)
print("Usuarios QA creados y entorno privado preparado")
