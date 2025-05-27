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
    print(f'Connected. Subscribing to: {MQTT_TOPIC}')
    client.subscribe(MQTT_TOPIC)


def on_message(client, userdata, message, properties=None):
    print(f"{dt.now()} Received message {message.payload} on topic '{message.topic}' with QoS {message.qos}")
    
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

        print(f'{driver.__name__}/{device}: {command}')
        driver.transmit_command(device, command)
    else:
        print(f'No driver for command: {command}')

def on_subscribe(client, userdata, mid, qos, properties=None):    
    print(f"{dt.now()} Subscribed with QoS {qos}")


def mqtt_gateway_433(host, port, username, password, txpin):
    client = mqtt.Client(client_id="mqtt433")#, protocol=mqtt.MQTTv311, clean_session=True)
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_subscribe = on_subscribe
    client.username_pw_set(username=username, password=password)
    client.connect(host=host, port=int(port), keepalive=60)

    drivers.tx433.TRANSMIT_PIN = txpin

    print('waiting....')
    client.loop_forever()


def main(args):

    load_drivers()

    print(os.getcwd())
    print(os.path.realpath(args.configfile))
    if not os.path.exists(args.configfile):
        logging.critical("Plugin configuration file missing {0}".format(args.configfile))
        sys.exit(-1)

    pluginconfig = configparser.ConfigParser()
    pluginconfig.read(args.configfile)
    txpin   = pluginconfig.get('MQTT433', 'TXPIN')
    enabled = pluginconfig.get('MQTT433', 'ENABLED')

    if enabled != "1":
        logging.warning("Plugin is not enabled in configuration - exiting")
        sys.exit(-1)

    for e,v in os.environ.items():
        logging.info(f'{e}={v}')

    configbase = os.environ.get("LBSCONFIG", default="config")
    configpath = os.path.join(configbase, "general.json")
    
    logging.info(f'Reading: {configpath}')
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

    
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Loxberry MQTT to RF433 Plugin.")
    parser.add_argument("--logfile", 
                        default="mqtt433.log",
                        help="specifies logfile path")
    parser.add_argument("--configfile", 
                        default="config\\mqtt433.cfg",
                        help="specifies plugin configuration file path")

    args = parser.parse_args()

    #
    # Configure logging
    #
    logging.getLogger().setLevel(logging.DEBUG)
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