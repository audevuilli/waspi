"""Module that contains the types used by waspi."""
import datetime
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional, Tuple
from uuid import UUID

#from data import Deployment, Sensor, SensorValue, Message
from waspi import data

class AudioRecorder(ABC):
    """Record audio from the microphone.

    The AudioRecorder is responsible for recording audio from the
    microphone.
    """

    @abstractmethod
    def record(self) -> data.Recording:
        """Record audio from the microphone and return the recording.

        The recording should be saved to a temporary file and the path
        to the file should be returned, along with the datetime, duration,
        and samplerate of the recording.

        The temporary file should be placed in memory.
        """

class Store(ABC):
    """The Store is responsible for storing the sensor readings locally.

    The store keeps track of all the sensors, readings, and deployment made.
    """

    @abstractmethod
    def get_current_deployment(self) -> data.Deployment:
        """Get the current deployment from the local filesystem."""

    @abstractmethod
    def store_deployment(self, deployment: data.Deployment) -> None:
        """Store the deployment locally."""

    @abstractmethod
    def store_sensor_value(self, sensor_value: data.SerialOutput) -> None:
        """Store the sensor values locally."""

    @abstractmethod
    def store_accel_recording(self, accel_recording: data.AccelRecording) -> None:
        """Store the sensor values locally."""


class SerialOutputMessageBuilder(ABC):
    """Build a message from the serial output. 
    
    The SerialOutput MessageBuilder is responsible for formatting the messages 
    to be sent over MQTT. 
    """

    @abstractmethod
    def build_message(
        self, 
        serial_output: data.SerialOutput, 
    ) -> List[data.Message]:
         """Build a message from the serial output."""


class AccelRecordingMessageBuilder(ABC):
    """Build a message from the recording.

    The RecordingMessageBuilder is responsible for building a message
    from the recording.
    """

    @abstractmethod
    def build_message(
        self,
        accel_recording: data.AccelRecording,
    ) -> data.Message:
        """Build a message from the recording."""


class Messenger(ABC):
    """Send messages to a remote server.

    The Messenger is responsible for sending messages to
    a remote server
    """

    @abstractmethod
    def send_message(self, message: data.Message) -> data.Response:
        """Send the message to a remote server."""


class MessageStore(ABC):
    """Keeps track of messages that have been sent."""

    @abstractmethod
    def get_unsent_messages(self) -> List[data.Message]:
        """Get the recordings that have not been synced to the server."""

    @abstractmethod
    def store_message(
        self,
        message: data.Message,
    ) -> None:
        """Register a message with the store."""

    @abstractmethod
    def store_response(
        self,
        response: data.Response,
    ) -> None:
        """Register a message response with the store."""
