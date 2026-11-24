from pathlib import Path
from copy import deepcopy
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt
from docx.oxml.ns import qn

ROOT = Path(__file__).resolve().parents[2]
TEMPLATE = Path(r"C:\Users\Sebas2hVR\Desktop\formato_ejecucion_guias_ape_estudiantes.docx")
OUTPUT = ROOT / "docs" / "INFORME_APE04_VACA_SEBASTIAN.docx"

doc = Document(TEMPLATE)

replacements = {
    "Tema de la guía práctica proporcionada por el docente": "Integración de aplicaciones orientadas a servicios mediante APIs REST JWT RabbitMQ NGINX y clientes multiplataforma",
    "(Especificado en la guía práctica proporcionada por el docente).": "Integrar siete proyectos mediante servicios REST seguros y mensajería asíncrona para comprobar una cadena comercial distribuida con evidencia reproducible.",
    "(Se recomiendan máximo 3)": "Implementar autenticación JWT y autorización por roles.\nComprobar idempotencia balanceo y recuperación de servicios.\nDocumentar resultados reales mediante Postman y las aplicaciones cliente.",
    "Detallada en la guía.": "Presencial y no presencial con ejecución práctica en un equipo Windows.",
    "Detalladas en la guía proporcionada por el docente.": "Mantener MySQL RabbitMQ Java FastAPI NGINX React PWA WinForms y JavaFX activos durante las verificaciones y conservar evidencia auténtica de cada caso.",
}

for p in doc.paragraphs:
    for old, new in replacements.items():
        if old in p.text:
            p.text = p.text.replace(old, new)

# Conserva la plantilla hasta el inicio de Actividades y sustituye el contenido posterior.
start = next(i for i, p in enumerate(doc.paragraphs) if "Actividades por desarrollar" in p.text)
body = doc._element.body
for p in list(doc.paragraphs[start:]):
    body.remove(p._element)

def heading(text):
    p = doc.add_paragraph(style="List Paragraph")
    r = p.add_run(text)
    r.bold = True
    r.font.size = Pt(12)
    r.font.color.rgb = None
    return p

def paragraph(text):
    p = doc.add_paragraph(text)
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_after = Pt(8)
    p.paragraph_format.line_spacing = 1.15
    return p

heading("Actividades desarrolladas")
intro = (
    "La práctica integra siete proyectos que colaboran mediante una arquitectura orientada a servicios.\n"
    "La API Java administra autenticación JWT y el catálogo de vehículos.\n"
    "FastAPI gestiona compradores y ventas con controles de idempotencia.\n"
    "RabbitMQ transporta los eventos comerciales hacia el servicio de notificaciones.\n"
    "NGINX centraliza las rutas y distribuye las solicitudes entre instancias Java.\n"
    "MySQL mantiene esquemas separados para reducir el acoplamiento entre servicios.\n"
    "WinForms React PWA y JavaFX permiten comprobar responsabilidades cliente diferentes.\n"
    "Postman se utiliza para ejecutar solicitudes positivas negativas y de seguridad.\n"
    "Git y GitHub conservan la línea base y la rama de integración de la práctica.\n"
    "Cada resultado se documenta mediante evidencia real sin exponer tokens ni contraseñas."
)
paragraph(intro)

figures = [
    (ROOT / "evidencias/fase-01/FIG_008_GITHUB_REPOSITORIO_BASE.png", "Se revisó el repositorio remoto que contiene los siete proyectos originales y el commit de línea base. Esta verificación permitió confirmar la estructura inicial antes de aplicar la integración en una rama independiente.", "Repositorio GitHub con los siete proyectos de la línea base."),
    (ROOT / "evidencias/fase-01/FIG_007_GIT_PUSH_RAMA_FEATURE.png", "Se creó la rama feature/ape04-fase1-integracion y se configuró su seguimiento remoto. La evidencia confirma que la rama fue publicada sin modificar directamente la rama principal.", "Publicación de la rama de integración en GitHub."),
    (ROOT / "evidencias/fase-01/FIG_001_XAMPP_MYSQL_ACTIVO.png", "Se comprobó la disponibilidad de MySQL como persistencia de los servicios. La instancia local quedó disponible para los esquemas de vehículos ventas y notificaciones.", "Servicio MySQL activo para la práctica."),
    (ROOT / "evidencias/fase-01/FIG_010_FASTAPI_MYSQL_WORKER.png", "Se preparó el esquema ventas_service mediante Alembic y se verificaron sus tablas. Después se inició el worker responsable de procesar tareas de ventas y publicación de eventos.", "Preparación de FastAPI MySQL y worker de ventas."),
    (ROOT / "evidencias/fase-01/FIG_009_NOTIFICACIONES_RABBITMQ_ACTIVO.png", "Se inició el servicio Java de notificaciones en el puerto 8181 y se confirmó su conexión con RabbitMQ en el puerto 5672. El registro demuestra que el consumidor quedó preparado para recibir eventos.", "Servicio de notificaciones conectado con RabbitMQ."),
    (ROOT / "evidencias/fase-01/FIG_011_NGINX_CONFIG_OK.png", "Se validó la configuración de NGINX mediante nginx -t. El resultado informó que la sintaxis era correcta y que el archivo de configuración podía utilizarse para el proxy y balanceo.", "Validación satisfactoria de la configuración NGINX."),
    (ROOT / "evidencias/fase-01/FIG_002_P01_HEALTH_JAVA_A_POSTMAN.png", "La prueba P01 comprobó la conectividad inicial de la API Java mediante GET al endpoint actuator health. Postman devolvió HTTP 200 y estado UP sin requerir credenciales.", "P01 conectividad inicial de la API Java con HTTP 200."),
    (ROOT / "evidencias/fase-02/FIG_004_E36_LOGIN_OPERADOR_200.png", "La prueba E36 ejecutó un inicio de sesión válido con rol OPERADOR. Postman recibió HTTP 200 y las aserciones confirmaron la presencia de un JWT sin mostrar su contenido en la evidencia.", "E36 autenticación OPERADOR aprobada con HTTP 200."),
    (ROOT / "evidencias/fase-02/FIG_005_E37_LOGIN_CONSULTA_200.png", "La prueba E37 autenticó correctamente al usuario con rol CONSULTA. La respuesta fue HTTP 200 y el panel de resultados ocultó los tokens para conservar la confidencialidad.", "E37 autenticación CONSULTA aprobada con HTTP 200."),
    (ROOT / "evidencias/fase-02/FIG_006_E38_FALLO_CHASIS_422.png", "La primera ejecución de E38 fue rechazada con HTTP 422 porque el chasis no tenía exactamente diecisiete caracteres. El fallo se conservó como evidencia real y motivó la corrección del generador de datos de prueba.", "E38 fallo real de validación del chasis con HTTP 422."),
    (ROOT / "evidencias/fase-03/FIG_012_WF_ESTADO_INICIAL.png", "Se abrió el cliente Windows Forms en su estado inicial para comprobar la disposición del campo JWT el área de resultados y el contador de vehículos. Esta captura registra el punto de partida antes de ampliar las operaciones administrativas.", "Estado inicial del cliente Windows Forms."),
    (ROOT / "evidencias/fase-03/FIG_013_P03_LISTADO_INICIAL.png", "La prueba P03 consultó el catálogo con un JWT válido y obtuvo HTTP 200. El cliente presentó dos vehículos persistidos con sus identificadores atributos precios y estado DISPONIBLE.", "P03 listado inicial de vehículos con HTTP 200."),
    (ROOT / "evidencias/fase-03/FIG_014_WF_SIN_TOKEN.png", "Se retiró el JWT de la barra compartida y se intentó utilizar la interfaz. La aplicación limpió la tabla y el contador y mostró un aviso para impedir solicitudes administrativas sin autenticación.", "Control del cliente Windows Forms al retirar el JWT."),
    (ROOT / "evidencias/fase-03/FIG_015_P02_FORMULARIO_VEHICULO.png", "Se incorporó un formulario específico para P02 con los campos exigidos por el contrato de creación de vehículos. La interfaz solicita marca modelo placa chasis de diecisiete caracteres año color y precio.", "Formulario de entrada para la prueba P02."),
    (ROOT / "evidencias/fase-03/FIG_016_P02_VEHICULO_CREADO_201.png", "La prueba P02 envió un vehículo Toyota Corolla con datos válidos mediante el JWT de la ventana principal. El servicio respondió HTTP 201 y el cliente confirmó la creación real del registro.", "P02 creación de vehículo aprobada con HTTP 201."),
    (ROOT / "evidencias/fase-03/FIG_017_P03_LISTADO_ACTUALIZADO.png", "Después de crear el vehículo se repitió P03 y el catálogo aumentó de dos a tres registros. El nuevo Toyota Corolla apareció con estado DISPONIBLE lo que demuestra coherencia entre escritura y lectura.", "P03 catálogo actualizado después de P02."),
    (ROOT / "evidencias/fase-03/FIG_018_P04_FORMULARIO_COMPRADOR.png", "Se abrió el formulario administrativo de P04 para registrar compradores mediante documento nombre y correo. El formulario reutiliza el JWT oculto de la ventana principal y dirige la solicitud a FastAPI a través de NGINX.", "Formulario de entrada para la prueba P04."),
    (ROOT / "evidencias/fase-03/FIG_019_P04_COMPRADOR_CREADO_201.png", "La prueba P04 registró un comprador con información válida y recibió HTTP 201. La confirmación visible demuestra que FastAPI aceptó y persistió la operación autenticada.", "P04 creación de comprador aprobada con HTTP 201."),
    (ROOT / "evidencias/fase-03/FIG_020_P06_VENTAS_200.png", "La prueba P06 consultó las ventas desde Windows Forms sin ofrecer una función de registro. La respuesta HTTP 200 mostró tres ventas completadas asociadas al comprador 4 y a los vehículos 4 5 y 6.", "P06 listado de tres ventas completadas con HTTP 200."),
]

for number, (image, explanation, caption) in enumerate(figures, 1):
    paragraph(explanation)
    if image.exists():
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.keep_with_next = True
        p.add_run().add_picture(str(image), width=Inches(6.15))
        c = doc.add_paragraph(f"Figura {number}. {caption}")
        c.alignment = WD_ALIGN_PARAGRAPH.CENTER
        c.paragraph_format.space_after = Pt(10)
        c.runs[0].italic = True

heading("Resultados obtenidos")
sentences = [
    "La práctica permitió construir una base funcional para integrar siete proyectos mediante servicios coordinados.",
    "Se conservó el repositorio original como referencia verificable del trabajo.",
    "La rama de integración separó los cambios realizados durante la ejecución.",
    "MySQL proporcionó persistencia independiente para los dominios principales.",
    "La API Java quedó disponible para autenticación y administración de vehículos.",
    "FastAPI organizó las operaciones de compradores y ventas.",
    "RabbitMQ estableció el canal asíncrono para los eventos comerciales.",
    "El servicio de notificaciones confirmó su conexión con el intermediario de mensajes.",
    "NGINX validó su configuración para centralizar las rutas del sistema.",
    "Postman permitió comprobar respuestas reales mediante solicitudes reproducibles.",
    "La conectividad inicial produjo una respuesta HTTP 200 con estado operativo.",
    "El inicio de sesión OPERADOR generó un token válido protegido en la evidencia.",
    "El inicio de sesión CONSULTA confirmó la separación efectiva de roles.",
    "Las pruebas negativas permitieron observar rechazos controlados del backend.",
    "La validación del chasis detectó un dato que no cumplía el contrato.",
    "El error HTTP 422 permitió corregir la generación de información de prueba.",
    "Windows Forms creó un vehículo y un comprador con respuestas HTTP 201.",
    "El listado actualizado confirmó la persistencia del nuevo vehículo.",
    "La consulta administrativa mostró tres ventas completadas sin registrarlas desde Windows Forms.",
    "En conjunto la práctica demostró cómo varios clientes y servicios pueden colaborar con contratos verificables."
]
paragraph(" ".join(sentences))

heading("Habilidades blandas empleadas en la práctica")
paragraph("Se aplicaron responsabilidad pensamiento crítico adaptabilidad comunicación técnica y resolución de problemas durante el diagnóstico la integración y la documentación de evidencias.")

heading("Conclusiones")
paragraph("La integración comprobada evidencia que la separación de responsabilidades facilita la evolución de los siete proyectos. Las pruebas reales ya ejecutadas confirman conectividad autenticación por roles y validación de entradas mientras los casos pendientes deben conservarse como pendientes hasta contar con su evidencia individual.")

heading("Recomendaciones")
paragraph("Se recomienda continuar la colección desde un entorno QA privado mantener ocultos los JWT y contraseñas y registrar cada caso inmediatamente después de su ejecución. También se debe repetir E38 con el chasis corregido y completar los casos de GUI balanceo mensajería y recuperación antes de cerrar el informe definitivo.")

heading("Referencias bibliográficas")
paragraph("[1] IETF, JSON Web Token JWT, RFC 7519, 2015.\n[2] RabbitMQ, RabbitMQ Documentation, 2026.\n[3] NGINX, NGINX Documentation, 2026.\n[4] Postman, Postman Learning Center, 2026.")

# Fuente base coherente con la plantilla.
for p in doc.paragraphs:
    for run in p.runs:
        run.font.name = "Arial"
        run._element.get_or_add_rPr().rFonts.set(qn("w:ascii"), "Arial")
        run._element.get_or_add_rPr().rFonts.set(qn("w:hAnsi"), "Arial")
        if run.font.size is None:
            run.font.size = Pt(10)

doc.save(OUTPUT)
print(OUTPUT)
