/*
  Waspi Arduino Sensor Code.
*/
#include "SerialTransfer.h"
#include "DFRobot_I2C_Multiplexer.h"
#include "HX711.h"
#include "Adafruit_SHT4x.h"
#include <DFRobot_SCD4X.h>

// Create the sensors objects 
SerialTransfer tfr;
HX711 scale;
DFRobot_I2C_Multiplexer I2CMultiplexer (&Wire, 0x70);
Adafruit_SHT4x sht45_0 = Adafruit_SHT4x();
Adafruit_SHT4x sht45_1 = Adafruit_SHT4x();
DFRobot_SCD4X scd41 = DFRobot_SCD4X();

// Reporting time interval
const unsigned int reportingInterval = 60000; // every minute

// Arduino Pins - LoadCell Sensor
const int loadCell_DoutPin = 9;
const int loadCell_SckPin = 10;

// LoadCell Calibration Factor - from SparkFun_HX711_Calibration sketch
float calibration_factor_scale_1 = 82750; 
float calibration_factor_scale_2 = 103800; 

// LoadCell Sensor value
float loadCell_Value;

// Temperature and Humidity values
float sht45_0_temperature, sht45_0_humidity;
float sht45_1_temperature, sht45_1_humidity; 

// SCD41 - CO2, Temperature and Humidity values
float scd41_temperature, scd41_humidity;
float scd41_co2ppm;

// ---- Setup Function ---- //
void setup() {

  // Initialize the HX711 load cell amplifier
  scale.begin(loadCell_DoutPin, loadCell_SckPin);
  //scale.set_scale(); 
  //scale.tare();	//Reset the scale to 0

  // Initialise the I2C Multiplexer
  I2CMultiplexer.begin();

  // Start the STH45_0, SHT45_1 sensors
  /**
   * @note See SHT45 Documentation: https://github.com/adafruit/Adafruit_SHT4X
  */
  sht45_0.begin();
  sht45_0.setPrecision(SHT4X_HIGH_PRECISION);
  sht45_0.setHeater(SHT4X_NO_HEATER);

  sht45_1.begin();
  sht45_1.setPrecision(SHT4X_HIGH_PRECISION);
  sht45_1.setHeater(SHT4X_NO_HEATER);

  // Start the SCD41 sensor
  /**
   * @note See SCD41 Documentation: https://github.com/DFRobot/DFRobot_SCD4X/
  */
  scd41.begin();
  scd41.enablePeriodMeasure(SCD4X_STOP_PERIODIC_MEASURE);
  scd41.setTempComp(0.0);
  scd41.setSensorAltitude(10);
  scd41.enablePeriodMeasure(SCD4X_START_LOW_POWER_MEASURE);

  // Start serial communication
  Serial.begin(115200);
  tfr.begin(Serial);

}

// ---- Serial Transfer Function ---- //
void sendPeriodicReport(){
  
  float sendSize = 0;

  // Pack loadCell data (float)
  sendSize = tfr.txObj(loadCell_Value, sendSize);

  // Pack SHT45_0 Temperature & Humidity
  sendSize = tfr.txObj(sht45_0_temperature, sendSize);
  sendSize = tfr.txObj(sht45_0_humidity, sendSize); 
  
  // Pack SHT45_1 Temperature & Humidity
  sendSize = tfr.txObj(sht45_1_temperature, sendSize);
  sendSize = tfr.txObj(sht45_1_humidity, sendSize);  

  // Pack SCD41 CO2, Temperature & Humidity
  sendSize = tfr.txObj(scd41_temperature, sendSize);
  sendSize = tfr.txObj(scd41_humidity, sendSize); 
  sendSize = tfr.txObj(scd41_co2ppm, sendSize);  


  // Send data (packet ID = 16) -> see callbacks w_serial.py
  tfr.sendData(sendSize, 0);
}


// ---- Loop Function ---- //
void loop(){

  // Get the starting time
  unsigned long startTime = millis();

  // --- Read and print sensors data
  
  // 1 - Load Cell
  scale.set_scale(calibration_factor_scale_2);
  loadCell_Value = scale.get_units(50);
  Serial.print("weight: ");
  Serial.println(loadCell_Value, 3);
  
  // 2 - Temperature & Humidity
  sensors_event_t hum, temp;

  // SHT45_#0
  I2CMultiplexer.selectPort(0);
  delay(100);

  sht45_0.getEvent(&hum, &temp);
  sht45_0_temperature = temp.temperature;
  sht45_0_humidity = hum.relative_humidity;

  Serial.print("temp_sht0: ");
  Serial.println(sht45_0_temperature);
  Serial.print("hum_sht0: ");
  Serial.println(sht45_0_humidity);

  // SHT45_#1
  I2CMultiplexer.selectPort(1);
  delay(100);

  sht45_1.getEvent(&hum, &temp);
  sht45_1_temperature = temp.temperature;
  sht45_1_humidity = hum.relative_humidity;

  Serial.print("temp_sht1: ");
  Serial.println(sht45_1_temperature);
  Serial.print("hum_sht1: ");
  Serial.println(sht45_1_humidity);
  
  // 3 - CO2 with Temperature & Humdity
  I2CMultiplexer.selectPort(2);
  delay(100);

  // SCD41
  bool isDataReady = false;

  // Wait until data is ready
  while (!isDataReady) {
    isDataReady = scd41.getDataReadyStatus();
    delay(50); // Poll every 50ms to avoid busy waiting
  }
  
  DFRobot_SCD4X::sSensorMeasurement_t data;
  scd41.readMeasurement(&data);
  scd41_temperature = data.temp;
  scd41_humidity = data.humidity;
  scd41_co2ppm = data.CO2ppm;

  Serial.print("temp_scd41: ");
  Serial.println(scd41_temperature);
  Serial.print("hum_scd41: ");
  Serial.println(scd41_humidity);
  Serial.print("co2_scd41: ");
  Serial.println(scd41_co2ppm);

  delay(200);

  // --- Send data to Serial
  sendPeriodicReport();

  // --- Stay in UART Tx loop until the next report
  while(true){
    unsigned long currentMillis = millis();
    if (currentMillis - startTime >= reportingInterval)
    return;
  }
}