"""Database models for the sqlite store."""
from datetime import datetime
from uuid import UUID

from pony import orm

from .types import BaseModels

__all__ = [
    "create_base_models",
]


def create_base_models(database: orm.Database) -> BaseModels:
    """Create the database and return the database and models."""
    BaseModel = database.Entity

    class Deployment(BaseModel):  # type: ignore
        _table_ = "deployment"

        id = orm.PrimaryKey(UUID, auto=True)
        """Unique ID of the deployment."""

        name = orm.Required(str)
        """Deployment name."""

        started_on = orm.Required(datetime, unique=True)
        """Datetime when the deployment started. Should be unique."""

        latitude = orm.Optional(float)
        """Latitude of the deployment site. Can be None if unknown."""

        longitude = orm.Optional(float)
        """Longitude of the deployment site. Can be None if unknown."""


    class SensorValue(BaseModel):  # type: ignore
        _table_ = "sensors_value"

        hwid = orm.Required(str)
        """The sensor hardware id to identify the sensor."""

        value = orm.Required(float)
        """Value of the sensor."""

        timestamp: orm.Required(float)
        """The datetime when the reading was made."""


    class SerialOutput(BaseModel):  # type: ignore
        _table_ = "sensors_reading"

        id = orm.PrimaryKey(UUID, auto=True)
        """Unique ID of the recording."""

        content = orm.Required(str)
        """Hwid of the sensor."""


    class AccelRecording(BaseModel):  # type: ignore
        _table_ = "accel_recording"

        id = orm.PrimaryKey(UUID, auto=True)
        """Unique ID of the recording."""

        hwid = orm.Optional(str, unique=False)
        """HWID of the recording file."""

        path = orm.Optional(str, unique=True)
        """Path to the recording file."""

        datetime = orm.Required(datetime, unique=True)
        """Datetime of the recording. Should be unique."""

    return BaseModels(
        Deployment=Deployment,  # type: ignore
        SensorValue=SensorValue, # type: ignore
        SerialOutput=SerialOutput, # type: ignore
        AccelRecording=AccelRecording,  # type: ignore
    )
