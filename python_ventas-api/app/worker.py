"""Procesador de operaciones pendientes y avisos no enviados."""
# Lee los argumentos del comando de ejecución.
import sys
# Controla la pausa entre reintentos.
import time
# Registra errores de la aplicación.
import logging
# Importa el componente local correspondiente a esta responsabilidad.
from app.db import SessionLocal
# Importa las consultas SQL de ventas desde la capa Repository.
from app.repositories.venta_repository import VentaRepository
# Importa el componente local correspondiente a esta responsabilidad.
from app.services.venta_service import procesar, notificar


# Ejecuta un solo barrido de ventas pendientes.
def ciclo():
    # Abre una sesión para consultar qué ventas requieren trabajo.
    with SessionLocal() as db:
        # Obtiene hasta 100 IDs PENDIENTE, EN_REVISION o avisos atrasados.
        ids = VentaRepository(db).pendientes()
    # Revisa cada venta una por una.
    for id in ids:
        # Empieza una sección controlada para recuperar los errores esperados.
        try:
            # Consulta o confirma en Java cuando la operación sigue incompleta.
            procesar(id)
            # Intenta reenviar avisos de ventas completadas.
            notificar(id)
        # Registra un fallo particular sin dejar de revisar las otras ventas.
        except Exception:
            # Imprime el error en la consola del trabajador.
            logging.exception("No se pudo conciliar venta %s", id)
# Solo arranca el bucle al ejecutar python -m app.worker.
if __name__ == "__main__":
    # Permite el modo continuo del trabajador.
    while True:
        # Empieza una sección controlada para recuperar los errores esperados.
        try:
            # Procesa un lote completo de operaciones.
            ciclo()
        # Registra un fallo particular sin dejar de revisar las otras ventas.
        except Exception:
            # Imprime el error en la consola del trabajador.
            logging.exception("Fallo de ciclo de recuperación")
        # Permite un ciclo de prueba en clase sin proceso infinito.
        if "--once" in sys.argv:
            # Termina tras ese ciclo solicitado.
            break
        # Espera 10 segundos entre ciclos continuos.
        time.sleep(10)
