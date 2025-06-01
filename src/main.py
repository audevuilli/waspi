import asyncio
from pathlib import Path

from waspi.components.program_orchestrator import ProgramOrchestrater
from waspi import config_mqtt


async def main():
    """Main function to run the orchestrator."""
    # Get the Configuration parameters
    config = {
        # Serial Configuration
        "serial_port": "/dev/ttyACM0",
        "serial_baud": 115200,
        "hwid_list": [
            "weight_scale",
            "temp_sht45_0",
            "hum_sht45_0",
            "temp_sht45_1",
            "hum_sht45_1",
            "temp_scd41",
            "hum_scd41",
            "co2ppm_scd41",
        ],
        # MQTT Configuration
        "mqtt_host": config_mqtt.DEFAULT_HOST,
        "mqtt_username": config_mqtt.DEFAULT_MQTTCLIENT_USER,
        "mqtt_password": config_mqtt.DEFAULT_MQTTCLIENT_PASS,
        "mqtt_port": config_mqtt.DEFAULT_PORT,
        "mqtt_clientid": config_mqtt.DEFAULT_CLIENTID,
        "mqtt_topic": config_mqtt.DEFAULT_TOPIC,
        # Accelerometer Configuration
        "accel_duration": 60.0,  # seconds
        "accel_samplerate": 16000,  # Hz
        "accel_channels": 2,  # Stereo
        "accel_dir": Path.home() / "storages" / "recordings" / "accel_rec",
        # Audio Configuration
        # "audio_duration": 30.0,  # seconds
        # "audio_samplerate": 44100,  # Hz
        # "audio_channels": 1,  # Mono
        # "audio_device_name": "WordForum USB: Audio",
        # "audio_dir": Path.home() / "storages" / "recordings" / "audio_mic",
        # Sqlite DB Configuration
        "db_path": Path.home() / "storages" / "waspi.db",
        "db_path_message": Path.home() / "storages" / "waspi_messages.db",
        # Timing Configuration
        "max_serial_timeout": 20,  # Maximum time to receive serial data and send to MQTT
        "break_time": 5,  # Sleep time before accel record
        "max_cycle_time": 5,  # Maximum overhead time for each cycle
    }

    # Create and run the program orchestrator
    orchestrator = ProgramOrchestrater(**config)
    await orchestrator.run_program_continuously()


if __name__ == "__main__":
    asyncio.run(main())
