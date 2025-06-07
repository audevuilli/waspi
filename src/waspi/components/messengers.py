"""Messengers for the acoupi package."""

import datetime
import logging
from typing import Optional

import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion

from waspi import data
from waspi.components.types import Messenger

logger = logging.getLogger(__name__)

__all__ = [
    "MQTTMessenger",
]


class MQTTMessenger(Messenger):
    """Messenger that sends messages via MQTT."""

    client: mqtt.Client
    """The MQTT client."""

    topic: str
    """The MQTT topic to send messages to."""

    timeout: int
    """Timeout for sending messages."""

    def __init__(
        self,
        host: str,
        username: str,
        topic: str,
        clientid: str,
        port: int = 1884,
        password: Optional[str] = None,
        timeout: int = 5,
    ) -> None:
        """Initialize the MQTT messenger."""
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.topic = topic
        self.timeout = timeout
        self.client = mqtt.Client(
            callback_api_version=CallbackAPIVersion.VERSION2,
            client_id=clientid,
        )
        self.client.username_pw_set(username, password)

    def _on_connect(self, client, userdata, flags, rc, properties=None):
        """Callback for when client connects."""
        if rc == 0:
            logger.info("MQTT client connected successfully")
        else:
            logger.error(f"MQTT client failed to connect, return code {rc}")

    def _on_disconnect(self, client, userdata, rc, properties=None):
        """Callback for when client disconnects."""
        logger.warning(f"MQTT client disconnected with return code {rc}")

    def _on_publish(self, client, userdata, mid, reason_code=None, properties=None):
        """Callback for when message is published."""
        logger.info(f"MQTT message published successfully, mid: {mid}")

    async def send_message(self, message: data.Message) -> data.Response:
        """Send a measurement message."""
        status = data.ResponseStatus.SUCCESS

        try:
            self.client.connect(self.host, port=self.port, keepalive=60)

            response = self.client.publish(
                self.topic,
                payload=message.content,
            )
            response.wait_for_publish(timeout=5)

            if not response.rc == mqtt.MQTT_ERR_SUCCESS:
                status = data.ResponseStatus.ERROR

            # Disconnect immediately after sending
            self.client.disconnect()

        except ValueError:
            status = data.ResponseStatus.ERROR
        except RuntimeError:
            status = data.ResponseStatus.FAILED

        received_on = datetime.datetime.now()

        return data.Response(
            message=message,
            status=status,
            received_on=received_on,
        )

    def disconnect(self):
        """Properly disconnect the MQTT client."""
        if self.client.is_connected():
            self.client.loop_stop()
            self.client.disconnect()
            logger.info("MQTT client disconnected")
