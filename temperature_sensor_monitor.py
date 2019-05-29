#!/usr/bin/python3
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
mqttc = AWSIoTMQTTClient("TemperatureSensor1_monitor") 
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

#Callback: MQTT Subscribe
def mqtt_subscribe_callback(client, userdata, message):
  logging.info(f'Received message on topic {message.topic} from {client} :')
  logging.info(message.payload)

#Register callback for MQTT Subscribe
mqttc.subscribe(
  config['Topics']['TEMPERATURE_SENSOR_1_TOPIC'],
  0,
  mqtt_subscribe_callback
)

logging.info('Now monitoring temperature...')
while True:
  time.sleep(1)