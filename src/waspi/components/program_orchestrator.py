import asyncio
import logging
from pathlib import Path
import time

from waspi.components.accel_rec import AccelRecorder
from waspi.components.sensor_manager import SerialReceiver
from waspi.components.message_factories import SensorValue_MessageBuilder
from waspi.components.messengers import MQTTMessenger
from waspi.components.message_stores.sqlite import SqliteMessageStore
from waspi.components.stores.sqlite import SqliteStore


# Setup the main logger
logging.basicConfig(
    filename="waspi.log",
    filemode="w",
    format="%(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("waspi")


##############################################
### CONFIGURATION PARAMETERS
class ProgramOrchestrater:
    """Orchestrates the main program flow: Serial reading,
    MQTT transmission and accelerometer recording in sequential order."""

    def __init__(
        self,
        # Serial Configuration
        serial_port: str,
        serial_baud: int,
        hwid_list: list,
        # MQTT Configuration
        mqtt_host: str,
        mqtt_username: str,
        mqtt_password: str,
        mqtt_port: int,
        mqtt_clientid: str,
        mqtt_topic: str,
        # Accelerometer Configuration
        accel_duration: float,
        accel_samplerate: int,
        accel_channels: int,
        accel_dir: Path,
        # Sqlite DB Configuration
        db_path: Path,
        db_path_message: Path,
        # Timing Configuration
        max_serial_timeout: int = 20,  # Maximum time to receive serial data and send to MQTT
        break_time: int = 5,  # Sleep time before accel record
        max_cycle_time: int = 5,  # Maximum overhead time for each cycle
    ):
        """Initialize the orchestrator with configuration parameters."""
        self.serial_receiver = SerialReceiver(
            port=serial_port, baud=serial_baud, hwid_list=hwid_list
        )
        self.mqtt_messenger = MQTTMessenger(
            host=mqtt_host,
            username=mqtt_username,
            password=mqtt_password,
            port=mqtt_port,
            clientid=mqtt_clientid,
            topic=mqtt_topic,
        )
        self.message_factory = SensorValue_MessageBuilder()
        self.accel_recorder = AccelRecorder(
            duration=accel_duration,
            samplerate=accel_samplerate,
            audio_channels=accel_channels,
            audio_dir=accel_dir,
        )
        self.db_store = SqliteStore(db_path=db_path)
        self.db_store_message = SqliteMessageStore(db_path=db_path_message)
        self.max_serial_timeout = max_serial_timeout
        self.break_time = break_time
        self.max_cycle_time = max_cycle_time

        # Ensure the audio directory exists
        accel_dir.mkdir(parents=True, exist_ok=True)

    async def process_serial_and_mqtt_phase(self):
        """Step 1: Read serial data and send to MQTT."""
        logger.info(" --- START SERIAL READ & MQTT Transmission --- ")
        phase_start = time.time()

        try:
            # Read serial data
            logger.info("Reading serial data...")
            # serial_task = asyncio.create_task(self.serial_receiver.get_SerialRx()) #serial_rx.get_SerialRx()
            serial_task = asyncio.create_task(self.serial_receiver.get_SerialRx())

            try:
                serial_output = await asyncio.wait_for(
                    serial_task, timeout=(self.max_serial_timeout - 5)
                )
            except asyncio.TimeoutError:
                logger.error(
                    f"Serial reading timed out after {self.max_serial_timeout-5}. Skipping this cycle."
                )
                return False, time.time() - phase_start

            if serial_output is None:
                logger.error("No serial output received. Skipping this cycle.")
                return False, time.time() - phase_start

            logger.info(f"Serial output received: {serial_output}")

            # Build and send MQTT Message
            logger.info("Building MQTT message...")
            message = await self.message_factory.build_message(serial_output)
            logger.info(f"Sending MQTT message: {message}")
            response = await self.mqtt_messenger.send_message(message)

            # Store the sensor values and MQTT response in the database
            self.db_store.store_sensor_value(serial_output)
            self.db_store_message.store_message(message)
            self.db_store_message.store_response(response)

            phase_duration = time.time() - phase_start

            if response.status.value == "SUCCESS":
                logger.info(
                    f"MQTT mesaage sent successfully in {phase_duration:.2f} seconds."
                )
                return True, phase_duration
            else:
                logger.error(f"Failed to send MQTT message: {response.status.value}")
                return False, phase_duration

        except Exception as e:
            phase_duration = time.time() - phase_start
            logger.error(f"Error in process_serial_and_mqtt_phase: {e}")
            return False, phase_duration

    async def break_time_phase(self):
        """Step 2: Sleep for a break time before recording accelerometer data."""
        logger.info(" --- START BREAK TIME PHASE --- ")
        await asyncio.sleep(self.break_time)

    async def process_accel_phase(self):
        """Step e: Record accelerometer data."""
        logger.info(" --- START ACCEL RECORDING PHASE --- ")
        phase_start = time.time()

        try:
            # Record accelerometer data
            recording = self.accel_recorder.record()

            phase_duration = time.time() - phase_start

            if recording is None:
                logger.error("Failed to record accelerometer data.")
                return False, phase_duration

            logger.info(f"Accelerometer data recorded successfully: {recording.path}")
            return True, phase_duration

        except Exception as e:
            phase_duration = time.time() - phase_start
            logger.error(f"Error in process_accel_phase: {e}")
            return False, phase_duration

    async def run_program_continuously(self):
        """Run the program continuously in a loop."""

        logger.info("Starting the main program loop...")
        try:
            while True:
                # Step 1: Process Serial and MQTT
                await self.process_serial_and_mqtt_phase()

                # Step 2: Break time before accelerometer recording
                await self.break_time_phase()

                # Step 3: Process Accelerometer
                await self.process_accel_phase()

                await asyncio.sleep(0.1)  # Very short sleep

        except KeyboardInterrupt:
            logger.info("Program interrupted by user. Exiting...")

        except Exception as e:
            logger.error(f"An error occurred in the main loop: {e}")
            raise
