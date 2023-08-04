"""Module that contains the types used by waspi."""
import datetime
from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
from uuid import UUID

#from data import Deployment, Sensor, SensorValue, Message
import data
#from data import *

class SerialReader(ABC):
    """ Read value from the sensor using pySerialTransfer."""
    
    @abstractmethod
    def serial_rx_coroutine(self):
        """ Get values from the sensors via SerialTransfer. 
        """


class SensorReader(ABC):
    """Read value from the sensor. 
    
    The SensorReader is responsible for reading values from the sensors.
    """
    @abstractmethod
    def get_sensor_reading(self) -> data.SensorValue:
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
    def get_current_deployment(self) -> data.Deployment:
        """Get the current deployment from the local filesystem."""

    @abstractmethod
    def store_deployment(self, deployment: data.Deployment) -> None:
        """Store the deployment locally."""

    @abstractmethod
    def get_sensors(self) -> data.Sensor:
        """Get the current sensors."""

    @abstractmethod
    def store_sensor(
        self, 
        sensor: data.Sensor, 
        deployment: Optional[data.Deployment] = None,
    ) -> None:
        """Store the sensor locally"""
    
    @abstractmethod
    def store_sensorvalue(
        self,
        value: data.SensorValue,
        sensor: Optional[data.Sensor] = None, 
        deployment: Optional[data.Deployment] = None,
    ) -> None:
        """Store the sensor values locally.

        Args:
            value: The value to store.
            sensor: The sensor that the value originated from.
            deployment: The deployment to store the sensor values under.
        """


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


class Messenger(ABC):
    """Send messages to a remote server.

    The Messenger is responsible for sending messages to
    a remote server
    """

    @abstractmethod
    def send_message(self, message: data.Message) -> data.Response:
        """Send the message to a remote server."""

