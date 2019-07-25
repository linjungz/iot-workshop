#!/usr/bin/python3
# temperature_sensor.py
# -- This is a demo program for AWS IoT MQTT Topic
# -- It simulates a temperature sensor that's connected to AWS IoT Core and publish sensor data to a specific MQTT topic
# Author: Randy Lin

import json
import time
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import configparser
import logging
import random
import time

logging.basicConfig(level = logging.INFO)

#Load configuration from config.ini
config = configparser.ConfigParser()
config.read('config.ini')

#Setup MQTT client and security certificates
mqttc = AWSIoTMQTTClient("TemperatureSensor1") 
mqttc.configureEndpoint(
  config['Endpoints']['BJS_IOT_ENDPOINT'],
  int(config['Endpoints']['BJS_IOT_ENDPOINT_PORT'])
)
mqttc.configureCredentials(
  config['Certs']['ROOT_CA'],
  config['Certs']['TEMPERATURE_SENSOR_1_PRIVATE_KEY'],
  config['Certs']['TEMPERATURE_SENSOR_1_CERT']
)

#Connect to IoT Core
mqttc.connect()
logging.info('MQTT Client Connected to IoT Core')

#Send sensor data to IoT Core infinitly

#Sensor data is randomized between 20 to 40
temp_val_min = 20
temp_val_max = 40

while True:
  temp_val = "{0:.1f}".format(random.uniform(temp_val_min, temp_val_max))
  payload = {
      'temperature' : temp_val
  }
  result = mqttc.publish(
    config['Topics']['TEMPERATURE_SENSOR_1_TOPIC'], 
    json.dumps(payload),
    0
  )
  logging.info(json.dumps(payload))
  if result == False:
    logging.error('Failed to publish message.')

  time.sleep(2)
