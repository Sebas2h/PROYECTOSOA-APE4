"""Sincroniza secretos internos locales con el entorno QA privado de Postman."""
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / ".runtime"
SECRETS_FILE = RUNTIME / "secrets.env"
ENV_FILE = RUNTIME / "APE04_LOCAL_QA_PRIVADO.postman_environment.json"

secrets = {}
for line in SECRETS_FILE.read_text(encoding="utf-8-sig").splitlines():
    if "=" in line and not line.lstrip().startswith("#"):
        key, value = line.split("=", 1)
        secrets[key.strip()] = value

notification_key = secrets.get("NOTIFICACIONES_KEY", "")
if not notification_key:
    raise SystemExit("Falta NOTIFICACIONES_KEY en .runtime/secrets.env")
if not ENV_FILE.exists():
    raise SystemExit(
        "Falta el entorno QA privado. Ejecuta primero la preparación de QA e impórtalo desde .runtime."
    )

environment = json.loads(ENV_FILE.read_text(encoding="utf-8-sig"))
values = {item["key"]: item for item in environment["values"]}
if "notificationKey" not in values:
    environment["values"].append({
        "key": "notificationKey", "value": "", "type": "default", "enabled": True
    })
    values = {item["key"]: item for item in environment["values"]}
values["notificationKey"]["value"] = notification_key
ENV_FILE.write_text(json.dumps(environment, indent=2), encoding="utf-8")
print("Entorno QA privado sincronizado. Clave interna no mostrada.")
