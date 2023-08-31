"""Module defining the SqliteStore class."""
import datetime
import json
from pathlib import Path
from typing import List, Optional, Tuple
from uuid import UUID
import asyncio

from pony import orm

from waspi import data
from waspi.components import types

from . import types as db_types
from .database import create_base_models


class SqliteStore(types.Store):
    """Sqlite store implementation.

    The store is used to store the sensor values, and accelerometer recordings
    locally. The data is stored in a sqlite database file in the given path.

    Under the hood, the store uses the Pony ORM to interact with the database.
    The database schema is defined in the database module and contains the
    following tables:

    - Sensor Value: Contains the sensor values. 

    - Accel Recording: Contains the recording information of the accelerometer. 
      Each recording has a datetime and a path.

    The store is thread-safe, and can be used from multiple threads simultaneously.
    """

    db_path: Path
    """Path to the database file."""

    database: orm.Database
    """The Pony ORM database object."""

    models: db_types.BaseModels
    """The Pony ORM models."""

    def __init__(self, db_path: Path) -> None:
        """Initialise the Sqlite Store.

        Will create a database file at the given path if it does not exist.

        Args:
            db_path: Path to the database file. Can be set to :memory: to use
                an in-memory database.

        """
        self.db_path = db_path
        self.database = orm.Database()
        self.models = create_base_models(self.database)
        self.database.bind(
            provider="sqlite",
            filename=str(db_path),
            create_db=True,
        )
        self.database.generate_mapping(create_tables=True)

    @orm.db_session
    def get_current_deployment(self) -> data.Deployment:
        """Get the current deployment.

        The current deployment is the one with the latest started_on datetime.

        If no deployment is found, a new deployment will be registered with the
        current datetime, and the latitude and longitude set to None.

        Returns:
            The current deployment
        """
        deployment = self._get_current_deployment()
        return data.Deployment(
            id=deployment.id,
            name=deployment.name,
            latitude=deployment.latitude,
            longitude=deployment.longitude,
            started_on=deployment.started_on,
        )

    @orm.db_session
    def store_deployment(self, deployment: data.Deployment) -> None:
        """Store the deployment locally.

        Args:
            deployment: The deployment to store
        """
        self._get_or_create_deployment(deployment)

    @orm.db_session
    def store_sensor_value(self, sensor_value: data.SerialOutput) -> None:
    #async def store_sensor_value(self, sensor_value: data.SensorValue) -> None:
        """Store the sensor values locally.

        Args:
            sensor_value: The sensor_value to store.
        """
        self._get_or_create_sensor_value(sensor_value)

    @orm.db_session
    def store_accel_recording(self, accel_recording: data.AccelRecording) -> None:
        """Store the accelerometer recordings path locally.
        
        Args:
            accel_recording: The accel_recording path to store.
        """
        db_accelrecording = self._get_or_create_accel_recording(accel_recording)


    @orm.db_session
    def _get_current_deployment(self) -> db_types.Deployment:
        """Get the current deployment in the database."""
        db_deployment = (
            orm.select(d for d in self.models.Deployment)
            .order_by(orm.desc(self.models.Deployment.started_on))
            .first()
        )

        if db_deployment is None:
            now = datetime.datetime.now()
            name = f'Deployment {now.strftime("%Y-%m-%d %H:%M:%S")}'
            db_deployment = self.models.Deployment(
                started_on=now,
                name=name,
                latitude=None,
                longitude=None,
            )
            orm.commit()

        return db_deployment


    #   -------------- FUNCTIONS RELATED to SENSOR_VALUE --------------   #
    @orm.db_session
    def _create_sensor_value(
        self,
        sensor_value: data.SerialOutput,
    ) -> db_types.SensorValue:
        """Create a sensor value."""
        db_sensor_value = self.models.SensorValue(
            id=sensor_value.id,
            content=sensor_value.content,
            datetime=sensor_value.datetime,
        )
        orm.commit()
        return db_sensor_value

    @orm.db_session
    def _get_or_create_sensor_value(
        self,
        sensor_value: data.SerialOutput,
    ) -> db_types.SerialOutput:
        """Get or create a recording."""
        try:
            return self._get_sensor_value_by_id(sensor_value.id)
        except ValueError:
            return self._create_sensor_value(sensor_value)

    @orm.db_session
    def _get_sensor_value_by_id(self, id: UUID) -> db_types.SerialOutput:
        """Get the sensor value by the id."""
        sensor_value: Optional[db_types.SerialOutput] = self.models.SerialOutput.get(
            id=id
        )
        if sensor_value is None:
            raise ValueError("No sensor value found")
        return sensor_value


    #   -------------- FUNCTIONS RELATED to ACCEL_RECORDING --------------   #
    @orm.db_session
    def _create_accel_recording(
        self,
        accel_recording: data.AccelRecording,
    ) -> db_types.SensorValue:
        """Create a sensor value."""
        db_accel_recording = self.models.AccelRecording(
            id=accel_recording.id,
            hwid=accel_recording.hwid,
            path=str(accel_recording.path),
            datetime=accel_recording.datetime,
        )
        orm.commit()
        return db_accel_recording

    @orm.db_session
    def _get_or_create_accel_recording(
        self,
        accel_recording: data.AccelRecording,
    ) -> db_types.AccelRecording:
        """Get or create a recording."""
        try:
            return self._get_accel_recording_by_id(accel_recording.id)
        except ValueError:
            return self._create_accel_recording(accel_recording)

    @orm.db_session
    def _get_accel_recording_by_id(self, id: UUID) -> db_types.AccelRecording:
        """Get the recording by the id."""
        accel_recording: Optional[db_types.AccelRecording] = self.models.AccelRecording.get(
            id=id
        )

        if accel_recording is None:
            raise ValueError("No accelerometer recording found")
        return accel_recording


    #   -------------- FUNCTIONS RELATED to DEPLOYMENT --------------   #
    @orm.db_session
    def _get_deployment_by_started_on(
        self, started_on: datetime.datetime
    ) -> db_types.Deployment:
        """Get the deployment by the started_on datetime."""
        deployment: Optional[db_types.Deployment] = self.models.Deployment.get(
            started_on=started_on
        )  # type: ignore

        if deployment is None:
            raise ValueError("No deployment found")

        return deployment

    @orm.db_session
    def _create_deployment(
        self,
        deployment: data.Deployment,
    ) -> db_types.Deployment:
        """Create a deployment."""
        db_deployment = self.models.Deployment(
            id=deployment.id,
            started_on=deployment.started_on,
            name=deployment.name,
            latitude=deployment.latitude,
            longitude=deployment.longitude,
        )
        orm.commit()
        return db_deployment

    @orm.db_session
    def _get_or_create_deployment(
        self, deployment: data.Deployment
    ) -> db_types.Deployment:
        """Get or create a deployment."""
        try:
            db_deployment = self._get_deployment_by_id(deployment.id)
        except ValueError:
            db_deployment = self._create_deployment(deployment)

        return db_deployment

    @orm.db_session
    def _get_deployment_by_id(self, id: UUID) -> db_types.Deployment:
        """Get the deployment by the id."""
        deployment: Optional[db_types.Deployment] = self.models.Deployment.get(
            id=id
        )

        if deployment is None:
            raise ValueError("No deployment found")

        return deployment
