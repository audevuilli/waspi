"""Module that contains the types used by waspi."""
import datetime
from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
from uuid import UUID

from data import Deployment, Sensor, SensorValue, Message


class SensorReader(ABC):
    """Read value from the sensor. 
    
    The SensorReader is responsible for reading values from the sensors.
    """
    @abstractmethod
    def get_sensor_reading(self) -> SensorValue:
        """ Read values from the sensors and return reading.

        The reading should be saved in flash memory and the value 
        of the reading should be returned, along with the datetime, 
        sensor hwid. 
        """

class Store(ABC):
    """The Store is responsible for storing the sensor readings locally.

    The store keeps track of all the sensors, readings, and deployment made.
    """

    @abstractmethod
    def get_current_deployment(self) -> Deployment:
        """Get the current deployment from the local filesystem."""

    @abstractmethod
    def store_deployment(self, deployment: Deployment) -> None:
        """Store the deployment locally."""

    @abstractmethod
    def get_sensors(self) -> Sensor:
        """Get the current sensors."""

    @abstractmethod
    def store_sensor(
        self, 
        sensor: Sensor, 
        deployment: Optional[Deployment] = None,
    ) -> None:
        """Store the sensor locally"""
    
    @abstractmethod
    def store_sensorvalue(
        self,
        value: SensorValue,
        sensor: Optional[Sensor] = None, 
        deployment: Optional[Deployment] = None,
    ) -> None:
        """Store the sensor values locally.

        Args:
            value: The value to store.
            sensor: The sensor that the value originated from.
            deployment: The deployment to store the sensor values under.
        """

class Messenger(ABC):
    """Send messages to a remote server.

    The Messenger is responsible for sending messages to
    a remote server
    """

    @abstractmethod
    def send_message(self, message: Message):
        """Send the message to a remote server."""


