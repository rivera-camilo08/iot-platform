import json
import logging
import time

import paho.mqtt.client as mqtt
from paho.mqtt.client import MQTTMessage

from app.core.config import settings
from app.db.session import SessionLocal
from app.repositories.device_repository import DeviceRepository
from app.repositories.telemetry_repository import TelemetryRepository
from app.services.device_service import DeviceService
from app.services.telemetry_service import TelemetryService

logger = logging.getLogger("iot_platform.mqtt")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)


def build_topic(mac_address: str) -> str:
    return settings.mqtt_topic_template.format(mac_address=mac_address)


def on_connect(client: mqtt.Client, userdata: dict, flags: dict, rc: int) -> None:
    if rc != 0:
        logger.error("MQTT broker connection failed", extra={"code": rc})
        return
    logger.info(
        "Conectado al broker MQTT",
        extra={"broker_host": settings.mqtt_broker_host, "broker_port": settings.mqtt_broker_port},
    )
    client.subscribe("devices/+/telemetry", qos=1)


def on_disconnect(client: mqtt.Client, userdata: dict, rc: int) -> None:
    if rc != 0:
        logger.warning(
            "Desconectado inesperadamente del broker MQTT",
            extra={"broker_host": settings.mqtt_broker_host, "broker_port": settings.mqtt_broker_port, "code": rc},
        )
    else:
        logger.info(
            "Desconectado del broker MQTT",
            extra={"broker_host": settings.mqtt_broker_host, "broker_port": settings.mqtt_broker_port},
        )


def on_message(client: mqtt.Client, userdata: dict, msg: MQTTMessage) -> None:
    payload_text = msg.payload.decode("utf-8", errors="ignore")
    logger.info("Mensaje MQTT recibido", extra={"topic": msg.topic, "payload": payload_text})
    try:
        payload = json.loads(payload_text)
    except json.JSONDecodeError as exc:
        logger.warning("Carga MQTT no es JSON válido", extra={"error": str(exc), "payload": payload_text})
        return

    try:
        topic_parts = msg.topic.split("/")
        mac_address = topic_parts[1]
    except IndexError:
        logger.warning("Tema MQTT inválido", extra={"topic": msg.topic})
        return

    device_token = payload.get("device_token")
    if not device_token:
        logger.warning("Falta device_token en payload MQTT", extra={"topic": msg.topic})
        return

    with SessionLocal() as db:
        device_repo = DeviceRepository(db)
        device_service = DeviceService(device_repo)
        device = device_service.validate_device_auth(mac_address, device_token)
        if not device:
            logger.warning("Autenticación de dispositivo fallida", extra={"mac_address": mac_address})
            return

        telemetry_service = TelemetryService(TelemetryRepository(db))
        try:
            telemetry_service.create_telemetry_records(device.id, payload)
            logger.info("Telemetría almacenada", extra={"device_id": str(device.id), "mac_address": mac_address})
        except ValueError as exc:
            logger.warning("No se guardó la telemetría MQTT", extra={"error": str(exc), "mac_address": mac_address})
        except Exception as exc:
            logger.error("Error al procesar telemetría MQTT", extra={"error": str(exc), "mac_address": mac_address})


def run() -> None:
    def make_client() -> mqtt.Client:
        client = mqtt.Client(client_id=settings.mqtt_client_id)
        client.on_connect = on_connect
        client.on_disconnect = on_disconnect
        client.on_message = on_message
        # If MQTT credentials are provided, use them
        if getattr(settings, "mqtt_username", None) and getattr(settings, "mqtt_password", None):
            client.username_pw_set(settings.mqtt_username, settings.mqtt_password)
        client.reconnect_delay_set(min_delay=1, max_delay=30)
        return client

    logger.info(
        "Iniciando listener MQTT",
        extra={
            "broker_host": settings.mqtt_broker_host,
            "broker_port": settings.mqtt_broker_port,
            "client_id": settings.mqtt_client_id,
        },
    )

    retry_delay = 5
    client = make_client()

    while True:
        try:
            client.connect(settings.mqtt_broker_host, settings.mqtt_broker_port, keepalive=60)
            client.loop_forever()
        except Exception as exc:
            logger.error(
                "Error en el listener MQTT",
                extra={"error": str(exc), "retry_delay": retry_delay},
            )
            time.sleep(retry_delay)
            retry_delay = min(retry_delay * 2, 60)
            client = make_client()


if __name__ == "__main__":
    run()
