"""
Node type Sprinkler main.py file.
Development version, for production use minified main.py
in sprinkler-firmware/main.py

Author: Shanmugathas Vigneswaran
email: vigneswaran.shanmugathas@outlook.fr
"""

import gc
import ujson
import time
import _thread
from ST7735 import TFT
from sysfont import sysfont
from umqtt.robust import MQTTClient
from settings import (
    tft,
    MQTT_SERVER,
    MQTT_PORT,
    WIFI_SSID
)
from utils import register_sprinkler
from sprinkler_io import read_sensors, water_valve_relay

gc.enable()

NODE_TYPE = "sprinkler"
NODE_TAG = 'orchid'

_SENSOR_TOPIC = NODE_TYPE + "/sensor"
_CONTROLLER_TOPIC = NODE_TYPE + "/controller"
_TFT = tft

registered = False
flow_dict = {
    "current": {
        "water_valve_signal": False,

    },
    "last": {
        "water_valve_signal": False,
    },
    "sensors": {},
    # if controller callback timeout
    # active soft fuse
    # soft will put all actuator security state
    # off or on : depends on actuator
    "updated_at": time.time(),
    'soft_fuse': False
}


def subscribe_controller():
    global flow_dict

    def callback(topic, msg):
        d = ujson.loads(msg)
        if d['tag'] == NODE_TAG:
            flow_dict['current']['water_valve_signal'] = d['water_valve_signal']
            flow_dict['updated_at'] = time.time()
            water_valve_relay.value(d['water_valve_signal'])

    c = MQTTClient(
        NODE_TYPE
        + "_"
        + NODE_TAG
        + "_SUB",
        MQTT_SERVER,
        MQTT_PORT
    )
    c.set_callback(callback)
    c.connect()
    c.subscribe(_CONTROLLER_TOPIC)
    while True:
        c.wait_msg()


def publish_sensors():
    global flow_dict

    c = MQTTClient(
        NODE_TYPE
        + "_"
        + NODE_TAG
        + "_PUB",
        MQTT_SERVER,
        MQTT_PORT
    )
    c.connect()
    while True:
        s = read_sensors(NODE_TAG)
        flow_dict['sensors'] = s
        c.publish(_SENSOR_TOPIC, ujson.dumps(s))


def init_display():
    global _TFT, registered
    wifi_ssid = WIFI_SSID
    if len(wifi_ssid) >= 14:
        wifi_ssid = WIFI_SSID[0:14]
    _TFT.fill(TFT.BLACK)
    _TFT.fillrect((0, 0), (128, 50), TFT.WHITE)
    _TFT.text((2, 2), "Wifi:" + wifi_ssid, TFT.BLACK, sysfont, 1.1, nowrap=False)
    _TFT.text((2, 10), "Node:" + NODE_TYPE, TFT.BLACK, sysfont, 1.1, nowrap=False)
    _TFT.text((2, 20), "Tag: " + NODE_TAG, TFT.BLACK, sysfont, 1.1, nowrap=False)
    if not registered:
        _TFT.text((2, 30), "WARNING:tag already registered !!!", TFT.RED, sysfont, 1.1, nowrap=False)
        _TFT.fillrect((0, 50), (128, 160), TFT.RED)


def update_display():
    global _TFT, flow_dict
    while True:
        # Flush dynamic part of screen
        _TFT.fillrect((0, 50), (128, 160), TFT.GRAY)
        if flow_dict['current']['water_valve_signal']:
            _TFT.fillrect((110, 50), (20, 10), TFT.GREEN)
            _TFT.text((2, 50), "Water valve on", TFT.BLACK, sysfont, 1.1, nowrap=False)
        else:
            _TFT.fillrect((110, 50), (20, 10), TFT.RED)
            _TFT.text((2, 50), "Water valve off", TFT.BLACK, sysfont, 1.1, nowrap=False)

        _TFT.text((2, 60), "Raw ADC: " + str(flow_dict['sensors']['soil_moisture_raw_adc']),
                  TFT.BLACK, sysfont, 1.1, nowrap=False)
        _TFT.text((2, 70), "Soil Moisture: " + str(flow_dict['sensors']['soil_moisture']),
                  TFT.BLACK, sysfont, 1.1, nowrap=False)

        _TFT.text((2, 70), "Soil Moisture: " + str(flow_dict['sensors']['soil_moisture']),
                  TFT.BLACK, sysfont, 1.1, nowrap=False)
        if flow_dict['soft_fuse']:
            _TFT.text((2, 80), "Soft fuse !", TFT.RED, sysfont, 1.1, nowrap=False)
        gc.collect()


def soft_fuse():
    global flow_dict
    while True:
        if (time.time() - flow_dict['updated_at']) > 1:
            water_valve_relay.value(False)
            flow_dict['current']['water_valve_signal'] = False
            flow_dict['soft_fuse'] = True
        else:
            flow_dict['soft_fuse'] = False


# =================================
# Register tag to Master
# =================================
registered = register_sprinkler(NODE_TAG)
init_display()

# =================================
# Subscription to controller
# =================================
_thread.start_new_thread(subscribe_controller, ())

# =================================
# Subscription to controller
# =================================
_thread.start_new_thread(publish_sensors, ())

# =================================
# Update TFT screen
# =================================
_thread.start_new_thread(update_display, ())

# =================================
# Soft fuse loop
# =================================
_thread.start_new_thread(soft_fuse, ())
