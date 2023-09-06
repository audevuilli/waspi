"""Data objects for waspi system.py"""
import datetime
from enum import IntEnum
from pathlib import Path
from typing import Dict, List, Optional
from uuid import UUID, uuid4
from pydantic import Field, BaseModel
from dataclasses import dataclass

class Deployment:
    """A Deployment class to capture information about the system.
    This includes latitude, longitude, deployment start.
    """

    id: UUID = Field(default_factory=uuid4)
    """The unique ID of the deployment."""

    name: str
    """User provided name of the deployment."""

    latitude: Optional[float] = None
    """The latitude of the site where the device is deployed."""

    longitude: Optional[float] = None
    """The longitude of the site where the device is deployed."""

    started_on: datetime.datetime = Field(default_factory=datetime.datetime.now)
    """The datetime when the system was deployed."""


class Sensor:
    """A device that collect data."""
    
    hwid: str
    """The sensor hardware id to identify the sensor."""

    unit: Optional[str]
    """The unit of the sensor reading."""


class SensorValue(BaseModel):
    """A reading from a sensor."""

    hwid: str
    """The sensor hardware id to identify the sensor."""

    value: float
    """The value of the sensor reading."""

    timestamp: float
    """The datetime when the reading was made."""


class SerialOutput(BaseModel):
    """The serial output."""
    
    id: UUID = Field(default_factory=uuid4)
    """The unique ID of the message."""

    content: Dict[str, SensorValue] = Field(default_factory=dict)
    """The message to be sent. Usually a JSON string."""


class AccelRecording(BaseModel):
    """A reading from a sensor."""
    
    id: UUID = Field(default_factory=uuid4)
    """The unique ID of the message."""

    datetime: datetime.datetime
    """The datetime when the recording was made"""

    hwid: str
    """The sensor hardware id to identify the sensor."""

    path: Optional[Path] = None
    """The path to the audio file in the local filesystem"""


class Message(BaseModel):
    """The message to be sent to remote server."""
    id: UUID = Field(default_factory=uuid4)
    """The unique ID of the message."""

    content: str
    """The message to be sent. Usually a JSON string."""

    created_on: datetime.datetime = Field(
        default_factory=datetime.datetime.now
    )
    """The datetime when the message was created."""


class ResponseStatus(IntEnum):
    """The status of a message."""

    SUCCESS = 0
    """The message was received successfully."""

    FAILED = 1
    """The message failed to send."""

    ERROR = 2
    """The message was sent, but there was an error."""

    TIMEOUT = 3
    """The message timed out."""


class Response(BaseModel):
    """The response from sending a message."""

    status: ResponseStatus
    """The status of the message."""

    message: Message
    """The message that was sent."""

    content: Optional[str] = None
    """The content of the response."""

    received_on: datetime.datetime = Field(
        default_factory=datetime.datetime.now
    )
    """The datetime the message was received."""
