#!/usr/bin/python3
# light.py
# -- This is a demo program for AWS IoT Shadow
# -- It simulates a light that's connected to AWS IoT Core and use Shadow for status control
# Author: Randy Lin

import json
import time
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient
import configparser
import logging
import random
import time

logging.basicConfig(format="%(asctime)s %(levelname)s [%(name)s] %(message)s", level = logging.INFO)

#Load configuration from config.ini
config = configparser.ConfigParser()
config.read('config.ini')

#Setup Shadow client and security certificates
shadowc = AWSIoTMQTTShadowClient('Light1')
shadowc.configureEndpoint(
  config['Endpoints']['BJS_IOT_ENDPOINT'],
  int(config['Endpoints']['BJS_IOT_ENDPOINT_PORT'])
)
shadowc.configureCredentials(
  config['Certs']['ROOT_CA'],
  config['Certs']['LIGHT_1_PRIVATE_KEY'],
  config['Certs']['LIGHT_1_CERT']
)

#Initialize Device Status
device_state_color = 'white'
device_state_brightness = '30'

#Connect to IoT Core
shadowc.connect()
logging.info('Shadow Client Connected to IoT Core')

#Create Device Shadow Handler with persistent subscription
deviceShadowHandler = shadowc.createShadowHandlerWithName('Light1', True)

#Callback: Shadow Update
def shadow_update_callback(payload, responseStatus, token):
    logging.info('========= Shadow Update Callback Begin ========')
    if responseStatus == 'timeout':
        logging.error(f'Shadow Update Request {token} time out!')
    if responseStatus == 'rejected':
        logging.info(f'Shadow Update Request {token} rejected.')    
    if responseStatus == 'accepted':
        logging.info(f'Shadow Update Request {token} accepted.')
    logging.info('========= Shadow Update Callback End ========')

#Callback: Shadow Get for Device Initialization
def shadow_get_init_callback(payload, responseStatus, token):
    logging.info('========= Shadow Get Callback for Device Initialization Begin ========')

    global device_state_color
    global device_state_brightness

    if responseStatus == 'timeout':
        logging.error(f'Shadow Get Request {token} time out!')

    if responseStatus == 'rejected':
        logging.info(f'Shadow Get Request {token} rejected.')
        logging.info('Maybe the Shadow is not created yet.')
    
    if responseStatus == 'accepted':
        logging.info(f'Shadow Get Request {token} accepted.')
        payloadDict = json.loads(payload)
        logging.info(payloadDict)
        logging.info('Now Got Shadow and Use it for Device Initialization')

        #Check if there's pending change
        if 'delta' in payloadDict['state']:
            logging.info('Got pending change in shadow and will apply it to device first')
            if 'color' in payloadDict['state']['delta']:
                device_state_color = payloadDict['state']['delta']['color']
                logging.info('Do some hardware work to change color to ' + device_state_color)
                logging.info('Pending change for color has been applied to device')
            if 'brightness' in payloadDict['state']['delta']:
                device_state_brightness = payloadDict['state']['delta']['brightness']
                logging.info('Do some hardware work to change brightness to ' + device_state_brightness)
                logging.info('Pending change for brightness has been applied to device')
            input('Now you can check the shadow document in AWS Console before I update it. Press Enter to continue.')
        else:
            logging.info('No delta found. No need to change')

    #Report Current State to Shadow
    current_device_state = {
        "state": {
            "reported": {
                "color": device_state_color,
                "brightness": device_state_brightness
            },
            "desired" : None
        }
    }
    logging.info('Report current status to shadow')
    deviceShadowHandler.shadowUpdate(json.dumps(current_device_state), shadow_update_callback, 5)
    logging.info('Completed Device Initialization.')
    logging.info('========= Shadow Get Callback for Device Initialization End ========')

    
#Callback: Shadow Delta
def shadow_delta_callback(payload, responseStatus, token):
    logging.info('========= Shadow Delta Callback Begin ========')

    global device_state_color
    global device_state_brightness

    logging.info('Got Shadow Delta.')
    payloadDict = json.loads(payload)
    logging.info(payloadDict)
    if 'color' in payloadDict['state']:
        device_state_color = payloadDict['state']['color']
        logging.info('Do some hardware work to change color to ' + device_state_color)
        logging.info('Pending change for color has been applied to device.')
    if 'brightness' in payloadDict['state']:
        device_state_brightness = payloadDict['state']['brightness']
        logging.info('Do some hardware work to change brightness to ' + device_state_brightness)
        logging.info('Pending change for brightness has been applied to device')

    input('Now you can check the shadow document in AWS Console before I update it. Press Enter to continue.')

    #Report Current State to Shadow
    current_device_state = {
        "state": {
            "reported": {
                "color": device_state_color,
                "brightness": device_state_brightness
            },
            "desired" : None
        }
    }
    logging.info('Report current status to shadow')
    deviceShadowHandler.shadowUpdate(json.dumps(current_device_state), shadow_update_callback, 5)
    logging.info('========= Shadow Delta Callback End ========')

#Main
#Register Callback for Shadow Delta
deviceShadowHandler.shadowRegisterDeltaCallback(shadow_delta_callback)
logging.info('Registered callback for delta')

#Power on the light and report status
logging.info("Now turn on the light and start device initialization.")
deviceShadowHandler.shadowGet(shadow_get_init_callback, 5)

while True:
    time.sleep(1)