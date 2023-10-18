/*
  Waspi Arduino Sensor Code.
*/
#include "SerialTransfer.h"
#include "DFRobot_I2C_Multiplexer.h"
#include "HX711.h"
#include "Adafruit_SHT4x.h"

// Create the sensors objects 
SerialTransfer tfr;
HX711 scale;
DFRobot_I2C_Multiplexer I2CMultiplexer (&Wire, 0x70);
Adafruit_SHT4x sht45_0 = Adafruit_SHT4x();
Adafruit_SHT4x sht45_1 = Adafruit_SHT4x();

// Reporting time interval
const unsigned int reportingInterval = 9900; // 10s

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


// ---- Setup Function ---- //
void setup() {

  // Initialize the HX711 load cell amplifier
  scale.begin(loadCell_DoutPin, loadCell_SckPin);
  //scale.set_scale(); 
  //scale.tare();	//Reset the scale to 0

  // Initialise the I2C Multiplexer
  I2CMultiplexer.begin();

  // Start the STH45_0 sensor
  sht45_0.begin();
  sht45_0.setPrecision(SHT4X_HIGH_PRECISION);
  sht45_0.setHeater(SHT4X_NO_HEATER);

  // Start the STH45_1 sensor
  sht45_1.begin();
  sht45_1.setPrecision(SHT4X_HIGH_PRECISION);
  sht45_1.setHeater(SHT4X_NO_HEATER);

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

  // Send data (packet ID = 16) -> see callbacks w_serial.py
  tfr.sendData(sendSize, 0);
}

// ---- SHT45 Read Values Function ---- //
void ReadI2C_SHT4xData(Adafruit_SHT4x &sensor, int sensorNumber) {

  // Define Temperature & Humidity
  sensors_event_t hum, temp;
  sensor.getEvent(&hum, &temp);

  Serial.print("Temperature in °C SHT_" + String(sensorNumber) + " ");
  Serial.println(temp.temperature);
  Serial.print("Humidity % RH SHT_" + String(sensorNumber) + " ");
  Serial.println(hum.relative_humidity);
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
  sht45_0.getEvent(&hum, &temp);
  sht45_0_temperature = temp.temperature;
  sht45_0_humidity = hum.relative_humidity;

  Serial.print("temp_sht0: ");
  Serial.println(sht45_0_temperature);
  Serial.print("hum_sht0: ");
  Serial.println(sht45_0_humidity);

  // SHT45_#1
  I2CMultiplexer.selectPort(1);
  sht45_1.getEvent(&hum, &temp);
  sht45_1_temperature = temp.temperature;
  sht45_1_humidity = hum.relative_humidity;

  Serial.print("temp_sht1: ");
  Serial.println(sht45_1_temperature);
  Serial.print("hum_sht1: ");
  Serial.println(sht45_1_humidity);
  
  delay(100);

  // --- Send data to Serial
  sendPeriodicReport();

  // --- Stay in UART Tx loop until the next report
  while(true){
    unsigned long currentMillis = millis();
    if (currentMillis - startTime >= reportingInterval)
    return;
  }
}

