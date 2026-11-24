"""Publicación durable de eventos de venta en RabbitMQ."""
import json
import pika
from app.config import (
    RABBITMQ_HOST, RABBITMQ_PORT, RABBITMQ_USER, RABBITMQ_PASSWORD,
    RABBITMQ_VHOST, RABBITMQ_EXCHANGE, RABBITMQ_ROUTING_KEY,
)


def publicar_venta(evento):
    credenciales = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
    parametros = pika.ConnectionParameters(
        host=RABBITMQ_HOST, port=RABBITMQ_PORT, virtual_host=RABBITMQ_VHOST,
        credentials=credenciales, socket_timeout=3, blocked_connection_timeout=3,
    )
    conexion = pika.BlockingConnection(parametros)
    try:
        canal = conexion.channel()
        canal.exchange_declare(exchange=RABBITMQ_EXCHANGE,
                               exchange_type="direct", durable=True)
        canal.basic_publish(
            exchange=RABBITMQ_EXCHANGE,
            routing_key=RABBITMQ_ROUTING_KEY,
            body=json.dumps(evento, separators=(",", ":"), ensure_ascii=False).encode(),
            properties=pika.BasicProperties(
                content_type="application/json", delivery_mode=2,
                message_id=evento["eventoId"], type="VENTA_COMPLETADA",
            ),
            mandatory=True,
        )
    finally:
        conexion.close()

