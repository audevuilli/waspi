"""Sqlite storage backend for waspi.

The SqliteStore class is used to store the sensor values and accelerometer recording 
paths locally. The data is stored in a sqlite database file in the given path.

Whenever sensor values or an accelerometer recording is made, it should be stored to
keep track of the data. To use the store, create an instance of the SqliteStore class,
and use the methods to store and retrieve data.

Example:
    Load the store:

    >>> from waspi.stores.sqlite import SqliteStore

    Create a new store instance, pointing to a database file:

    >>> store = SqliteStore("waspi.db")

    Get the current deployment:

    >>> deployment = store.get_current_deployment()
    >>> deployment
    Deployment(id=1, started_on=datetime.datetime(2021, 1, 1, 0, 0), latitude=0, longitude=0)

    Create a new deployment:

    >>> deployment = Deployment(
    ...     started_on=datetime.datetime(2021, 1, 1, 0, 0),
    ...     device_id="0000000000000000",
    ...     latitude=0.0,
    ...     longitude=0.0,
    ... )
    >>> store.store_deployment(deployment)

    Store a new sensor value:

    >>> sensor_value = SensorValue(
    ...     datetime=datetime.datetime(2021, 1, 1, 0, 0),
    ...     hwid=temperature0,
    ...     value=19.5,
    ... )
    >>> store.store_sensor_value(sensor_value)

    Store a new detection:

    >>> detection = Detection(
    ...     species_name="species",
    ...     probability=0.5,
    ... )
    >>> store.store_detections(recording, [detection])

"""
# TODO: Update sqlite store documentation
from acoupi.components.stores.sqlite.store import SqliteStore

__all__ = [
    "SqliteStore",
]
