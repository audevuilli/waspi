"""Types for waspi ORM models."""
from datetime import datetime
from typing import Dict, List, NamedTuple, Optional
from uuid import UUID

from pony.orm import Json, core

__all__ = [
    "BaseModels",
    "Deployment",
    "SensorValue",
    "SerialOutput",
    "AccelRecording",
]


class Deployment(core.EntityMeta):
    """Deployment ORM model."""

    id: UUID
    """Unique ID of the deployment."""

    name: str
    """Deployment name"""

    started_on: datetime
    """Datetime when the deployment started. Should be unique."""

    latitude: Optional[float]
    """Latitude of the deployment site. Can be None if unknown."""

    longitude: Optional[float]
    """Longitude of the deployment site. Can be None if unknown."""


class SensorValue(core.EntityMeta):
    """A reading from a sensor."""

    hwid: str
    """The sensor hardware id to identify the sensor."""

    value: float
    """The value of the sensor reading."""

    timestamp: float
    """The datetime when the reading was made."""


class SerialOutput(core.EntityMeta):
    """Recording ORM model."""

    id: UUID
    """Unique ID of the sensor value"""

    datetime: datetime
    """Datetime of the sensor value. Should be unique"""

    content: str
    """The sensor hardware id to identify the sensor."""


class AccelRecording(core.EntityMeta):
    """Predicted tag ORM model."""

    id: UUID
    """Unique ID of the accelerometer recording"""

    hwid: str
    """Id of the accelerometer"""

    datetime: datetime
    """Datetime of the recording."""

    path: Optional[str]
    """Path to the recording file."""


class BaseModels(NamedTuple):
    """Container for models."""

    Deployment: Deployment
    SensorValue: SensorValue
    SerialOutput: SerialOutput
    AccelRecording: AccelRecording