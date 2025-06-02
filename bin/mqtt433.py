#!/usr/bin/env python3

import configparser
import json
import logging
import sys
import os
import argparse


#import gateway

import paho.mqtt.client as mqtt
from datetime import datetime as dt
import re

import drivers
import pkgutil
import importlib

MQTT_TOPIC = 'mqtt433/#'
DRIVERS = {}

def load_drivers():
    drivers_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'drivers')
    sys.path.insert(0, drivers_path)

    #
    # build driver module list
    #
    for module in pkgutil.iter_modules(drivers.__path__):
        m = importlib.import_module(f'drivers.{module.name}', package='drivers')
        if hasattr(m, 'transmit_command'):
            logging.info(f'loading driver: {module.name}')
            print(f'loading driver: {module.name}')
            DRIVERS[module.name] = m


def on_connect(client, userdata, flags, reason_code, properties=None):   
    logging.info(f'Connected. Subscribing to: {MQTT_TOPIC}')
    client.subscribe(MQTT_TOPIC)


def on_message(client, userdata, message, properties=None):
    logging.info(f"{dt.now()} Received message {message.payload} on topic '{message.topic}' with QoS {message.qos}")
    
    #
    # topic structure:
    #   mqtt433/<driver>/<device>/command value
    # i.e.
    #   mqtt433/westin/fan/command speed3
    #
    m = re.search(r'^mqtt433/([a-zA-Z0-9_]+)\/([a-zA-Z0-9_]+)\/command$', message.topic)
    if m and m.group(1) in DRIVERS.keys():
        driver  = DRIVERS[m.group(1)]
        device  = m.group(2)
        command = message.payload.decode('utf-8')

        logging.info(f'{driver.__name__}/{device}: {command}')
        driver.transmit_command(device, command)
    else:
        logging.warning(f'No driver for command: {command}')

def on_subscribe(client, userdata, mid, qos, properties=None):    
    logging.info(f"{dt.now()} Subscribed with QoS {qos}")


def mqtt_gateway_433(host, port, username, password, txpin):
    client = mqtt.Client(client_id="mqtt433")#, protocol=mqtt.MQTTv311, clean_session=True)
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_subscribe = on_subscribe
    client.username_pw_set(username=username, password=password)
    client.connect(host=host, port=int(port), keepalive=60)

    drivers.tx433.TRANSMIT_PIN = txpin

    logging.info('entering message loop....')
    client.loop_forever()


def main(args):

    load_drivers()

    print(os.path.realpath(args.configfile))
    if not os.path.exists(args.configfile):
        logging.critical("Plugin configuration file missing {0}".format(args.configfile))
        sys.exit(-1)

    pluginconfig = configparser.ConfigParser()
    pluginconfig.read(args.configfile)
    txpin   = pluginconfig.get('MQTT433', 'TXPIN')
    enabled = pluginconfig.get('MQTT433', 'ENABLED')

    if enabled != "1":
        logging.critical("Plugin is not enabled in configuration - exiting")
        sys.exit(-1)

    #for e,v in os.environ.items():
    #    logging.info(f'{e}={v}')

    configbase = os.environ.get("LBSCONFIG", default="config")
    configpath = os.path.join(configbase, "general.json")
    
    logging.info(f'Reading config: {configpath}')
    
    if not os.path.exists(configpath):
        logging.critical("Plugin configuration file missing {0}".format(configpath))
        sys.exit(-1)

    with open(configpath, "r") as f:
        data = json.load(f)

    if not data["Mqtt"]:
        logging.critical("MQTT Broker not found - please check plugin configuration")
        sys.exit(-1)
        
    mqttd = data["Mqtt"]
    logging.info(f'MQTT Broker: {mqttd["Brokeruser"]}@{mqttd["Brokerhost"]}:{int(mqttd["Brokerport"])}')
    
    mqtt_gateway_433(mqttd["Brokerhost"], int(mqttd["Brokerport"]),
                        mqttd["Brokeruser"], mqttd["Brokerpass"], 
                        txpin)

def lox_loglevel(loxlevel):
    if loxlevel == 3: return logging.ERROR
    if loxlevel == 4: return logging.WARNING
    if loxlevel == 6: return logging.INFO
    if loxlevel == 7: return logging.DEBUG
    if loxlevel == 0 or loxlevel == -1: return logging.NOTSET    
    print("Unknown log level: {loxlevel}")
    return logging.NOTSET    
    
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Loxberry MQTT to RF433 Plugin.")
    parser.add_argument("--logfile", 
                        default="mqtt433.log",
                        help="specifies logfile path")
    parser.add_argument("--loglevel", 
                        default=3, # error
                        type=int,
                        help="specifies logfile path")
    parser.add_argument("--configfile", 
                        default="config\\mqtt433.cfg",
                        help="specifies plugin configuration file path")

    args = parser.parse_args()

    #
    # Configure logging
    #
    logging.getLogger().setLevel(lox_loglevel(args.loglevel))
    logging.basicConfig(filename=args.logfile,
                        filemode='w', 
                        level=logging.DEBUG,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',)

    # define a Handler which writes INFO messages or higher to the sys.stderr
    console = logging.StreamHandler()
    console.setLevel(logging.NOTSET)

    # add the handler to the root logger
    logging.getLogger('').addHandler(console)
    logging.info("using plugin log file {0}".format(args.logfile))

    # 
    try:
        main(args)
    except Exception as e:
        logging.critical(e, exc_info=True)