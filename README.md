# Waspi IoT Monitoring System

Work in progress. Any questions, suggestions contact aude.vuilliomenet.18@ucl.ac.uk 

WasPi is a real-time monitoring system used to study the activity of wasp nests. The system is made of two parts; the environmental sensors node and the audio and vision logging node. 

The following diagram illustrates the different components of Waspi. 

Overview of the system

<img src="images/electronics_top_01.jpeg" width="120">
<img src="images/waspi_system_overview.png" width="220">
<img src="images/setup_top_02.jpeg" width="120">


## Wasp Nest Env. Sensor Nodes

### Hardware
Microcontrollers 
- Arduino Uno
- Raspberry Pi 3B+

Sensors
- SHT45 Temperature and Humidity Sensor (Adafruit): [Adafruit Wiki](https://learn.adafruit.com/adafruit-sht40-temperature-humidity-sensor), [Sensirion Datasheet](https://sensirion.com/resource/datasheet/sht4x)
- 805M1-0020 Accelerometer (TE Connectivity): [TE Datasheet](https://tinyurl.com/2p9mrhd9)
- SBS-PT-50/2 [Weight Scale](https://www.amazon.co.uk/Steinberg-Systems-SBS-PT-50-Different-functions/dp/B01G713J94)

Others
- LM386 Power Amplifier: [TI Datasheet](https://www.ti.com/lit/gpn/lm386)
- MCP3002 10-bit ADC: [Microchip Datasheet](https://ww1.microchip.com/downloads/aemDocuments/documents/APID/ProductDocuments/DataSheets/21294E.pdf)
- SBS-PT-50/2 [Weight Scale](https://www.amazon.co.uk/Steinberg-Systems-SBS-PT-50-Different-functions/dp/B01G713J94)
- HX711 Load Cell Amplifier: [Sparkfun](https://www.sparkfun.com/products/13879), [Datasheet](https://tinyurl.com/925rx3k2)

Power
- 100W Solar Panel: [TGR-PS-SP120](https://cpc.farnell.com/tiger-power-supplies/tgr-ps-sp120/portable-power-station-solar-panel/dp/PL16994)
- 320Wh Portable Power Station: [TGR-PS-300](https://cpc.farnell.com/tiger-power-supplies/tgr-ps-300/portable-power-station-300w-600w/dp/PL16991)

To be implemented
- SGP40 TVOC/eCO2 Sensor (Adafruit): [Adafruit Wiki](https://learn.adafruit.com/adafruit-sgp40), [Sensirion Datasheet](https://developer.sensirion.com/fileadmin/user_upload/customers/sensirion/Dokumente/9_Gas_Sensors/Datasheets/Sensirion_Gas_Sensors_Datasheet_SGP40.pdf)
- MEMS Microphone - [ICS-40190](https://www.sparkfun.com/products/18011), [VM2020](https://www.sparkfun.com/products/21537), [SPH0645LM4H](https://www.adafruit.com/product/3421) 
- Current & Power Sensor: [INA260 Adafruit Board](https://cdn-learn.adafruit.com/downloads/pdf/adafruit-ina260-current-voltage-power-sensor-breakout.pdf), [PAC1932 Microchip Datasheet](https://tinyurl.com/yxxvpz79) 

### Software
- [arduino_waspi.ino](/arduino/arduino_waspi/arduino_waspi.ino)


