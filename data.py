"""Data objects for waspi system.py"""
import datetime
from typing import List, Optional, Tuple
from uuid import UUID, uuid4
from pydantic import Field
from dataclass import dataclass

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

@dataclass
class SensorValue:
    """A reading from a sensor."""
    
    datetime: datetime.datetime
    """The datetime when the reading was made."""

    hwid: str
    """The sensor hardware id to identify the sensor."""

    value: float
    """The value of the sensor reading."""

    deployment: Optional[Deployment]
    """The deployment that the sensor readings belong to."""


class Message:
    """The message to be sent to remote server."""
    id: UUID = Field(default_factory=uuid4)
    """The unique ID of the message."""

    content: str
    """The message to be sent. Usually a JSON string."""

    created_on: datetime.datetime = Field(
        default_factory=datetime.datetime.now
    )
    """The datetime when the message was created."""