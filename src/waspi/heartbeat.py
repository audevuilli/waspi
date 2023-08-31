import paho.mqtt.publish as publish
import datetime
import time
import logging

import config_mqtt


# Setup the main logger
logging.basicConfig(
    filename="heartbeat.log",
    filemode="w",
    format="%(levelname)s - %(message)s",
    level=logging.INFO,
)

starttime=time.time()

while True:
  payload = "" + datetime.datetime.now().strftime("%Y-%m-%d") + "T" + datetime.datetime.now().strftime("%X")
  sleeper = 360.0 - ((time.time() - starttime) % 360.0)
  time.sleep(sleeper)
  try:
    mqtt_auth = { 'username': config_mqtt.DEFAULT_MQTTCLIENT_USER, 'password': config_mqtt.DEFAULT_MQTTCLIENT_PASS }
    publish.single(config_mqtt.DEFAULT_TOPIC, payload, hostname=config_mqtt.DEFAULT_HOST, port=config_mqtt.DEFAULT_PORT, auth=mqtt_auth)
  except:
    logging.info("No connection")