import asyncio
import serial
import serial.tools.list_ports
from pathlib import Path
import logging

from waspi.components.program_orchestrator import (
    ProgramOrchestrater,
    SyncAwareOrchestrator,
)
from waspi.components.lockfile_coordinator import LockFileCoordinator
from waspi import config_mqtt

# Setup enhanced logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("waspi.main")


def debug_serial_connection(port: str, baud: int):
    """Debug serial connection issues."""
    logger.info("🔍 Starting serial connection debugging...")
    
    # List all available serial ports
    logger.info("📋 Available serial ports:")
    ports = serial.tools.list_ports.comports()
    if not ports:
        logger.warning("❌ No serial ports found!")
        return False
    
    for port_info in ports:
        logger.info(f"   📌 {port_info.device} - {port_info.description}")
        if hasattr(port_info, 'hwid'):
            logger.info(f"      Hardware ID: {port_info.hwid}")
    
    # Check if the specified port exists
    if not any(p.device == port for p in ports):
        logger.error(f"❌ Specified port {port} not found in available ports!")
        return False
    
    # Try to open the serial connection
    logger.info(f"🔌 Attempting to connect to {port} at {baud} baud...")
    try:
        with serial.Serial(port, baud, timeout=1) as ser:
            logger.info(f"✅ Successfully opened serial connection")
            logger.info(f"   Port: {ser.port}")
            logger.info(f"   Baud rate: {ser.baudrate}")
            logger.info(f"   Timeout: {ser.timeout}")
            logger.info(f"   Is open: {ser.is_open}")
            
            # Try to read some data
            logger.info("📖 Attempting to read data (5 second test)...")
            import time
            start_time = time.time()
            data_received = False
            
            while time.time() - start_time < 5:
                if ser.in_waiting > 0:
                    data = ser.readline()
                    logger.info(f"📨 Received data: {data}")
                    data_received = True
                    break
                time.sleep(0.1)
            
            if not data_received:
                logger.warning("⚠️ No data received in 5 seconds")
                logger.info("💡 Possible issues:")
                logger.info("   - Device not connected")
                logger.info("   - Wrong baud rate")
                logger.info("   - Device not sending data")
                logger.info("   - Hardware issue")
            
            return True
            
    except serial.SerialException as e:
        logger.error(f"❌ Failed to open serial connection: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error during serial test: {e}")
        return False


async def test_serial_receiver(config):
    """Test the SerialReceiver component specifically."""
    from waspi.components.sensor_manager import SerialReceiver
    
    logger.info("🧪 Testing SerialReceiver component...")
    
    try:
        serial_receiver = SerialReceiver(
            port=config["serial_port"],
            baud=config["serial_baud"],
            hwid_list=config["hwid_list"]
        )
        
        logger.info("✅ SerialReceiver created successfully")
        
        # Test with different timeouts
        for timeout in [5, 10, 15]:
            logger.info(f"🕐 Testing with {timeout}s timeout...")
            try:
                serial_task = asyncio.create_task(serial_receiver.get_SerialRx())
                result = await asyncio.wait_for(serial_task, timeout=timeout)
                logger.info(f"✅ Got data in {timeout}s: {result}")
                return True
            except asyncio.TimeoutError:
                logger.warning(f"⏰ Timeout after {timeout}s")
            except Exception as e:
                logger.error(f"❌ Error during {timeout}s test: {e}")
        
        return False
        
    except Exception as e:
        logger.error(f"❌ Failed to create SerialReceiver: {e}")
        return False


async def main():
    """Main function to run the orchestrator with enhanced debugging."""
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
        "accel_samplerate": 44100,  # Hz
        "accel_channels": 2,  # Stereo
        "accel_dir": Path.home() / "storages" / "recordings" / "accel_rec",
        # Sqlite DB Configuration
        "db_path": Path.home() / "storages" / "waspi.db",
        "db_path_message": Path.home() / "storages" / "waspi_messages.db",
        # Timing Configuration
        "max_serial_timeout": 20,  # Maximum time to receive serial data and send to MQTT
        "break_time": 5,  # Sleep time before accel record
        "max_cycle_time": 5,  # Maximum overhead time for each cycle
    }

    logger.info("🔧 Starting application with enhanced debugging...")
    
    # Debug serial connection first
    logger.info("=" * 50)
    serial_ok = debug_serial_connection(config["serial_port"], config["serial_baud"])
    
    if not serial_ok:
        logger.error("❌ Serial connection test failed. Exiting.")
        return
    
    logger.info("=" * 50)
    
    # Test SerialReceiver component
    receiver_ok = await test_serial_receiver(config)
    
    if not receiver_ok:
        logger.error("❌ SerialReceiver test failed. Please check your SerialReceiver implementation.")
        logger.info("💡 Common issues to check:")
        logger.info("   - SerialReceiver.get_SerialRx() method implementation")
        logger.info("   - Data parsing logic in SerialReceiver")
        logger.info("   - Hardware ID matching logic")
        return
    
    logger.info("=" * 50)
    logger.info("✅ All tests passed! Starting main application...")

    # Create and run the program orchestrator
    orchestrator = ProgramOrchestrater(**config)
    # Instantiate the coordinator
    coordinator = LockFileCoordinator()

    # Create a sync-aware orchestrator to handle lock file coordination
    sync_orchestrator = SyncAwareOrchestrator(
        orchestrator=orchestrator,
        coordinator=coordinator,
    )
    await sync_orchestrator.run_continuous_with_sync_awareness()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("⛔ Application stopped by user")
    except Exception as e:
        logger.error(f"💥 Application crashed: {e}")
        logger.error(f"Exception type: {type(e).__name__}")
        raise
