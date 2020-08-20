"""
Node type Water main.py file.
Development version, for production use minified main.py
in water-firmware/main.py

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

from settings import tft
from settings import MQTT_SERVER
from settings import MQTT_PORT
from settings import WIFI_SSID
from settings import __water_firmware_version__

from water_io import read_sensors
from water_io import water_pump_relay
from water_io import nutrient_pump_relay
from water_io import ph_downer_pump_relay

gc.enable()

NODE_TYPE = "water"
_SENSOR_TOPIC = NODE_TYPE + "/sensor"
_CONTROLLER_TOPIC = NODE_TYPE + "/controller"
_TFT = tft

registered = False
flow_dict = {
    "current": {
        "water_pump_signal": False,
        "nutrient_pump_signal": False,
        "ph_downer_pump_signal": False,
    },
    "last": {
        "water_pump_signal": False,
        "nutrient_pump_signal": False,
        "ph_downer_pump_signal": False,
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
        flow_dict['current']['water_pump_signal'] = d['water_pump_signal']
        flow_dict['current']['nutrient_pump_signal'] = d['nutrient_pump_signal']
        flow_dict['current']['ph_downer_pump_signal'] = d['ph_downer_pump_signal']
        flow_dict['updated_at'] = time.time()
        water_pump_relay.value(d['water_pump_signal'])
        nutrient_pump_relay.value(d['nutrient_pump_signal'])
        ph_downer_pump_relay.value(d['ph_downer_pump_signal'])

    c = MQTTClient(
        NODE_TYPE
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
        + "_PUB",
        MQTT_SERVER,
        MQTT_PORT
    )
    c.connect()
    while True:
        s = read_sensors()
        flow_dict['sensors'] = s
        c.publish(_SENSOR_TOPIC, s['influx_message'])


def init_display():
    global _TFT
    wifi_ssid = WIFI_SSID
    if len(wifi_ssid) >= 14:
        wifi_ssid = WIFI_SSID[0:14]
    _TFT.fill(TFT.BLACK)
    _TFT.fillrect((0, 0), (128, 50), TFT.WHITE)
    _TFT.text((2, 2), "Wifi:" + wifi_ssid, TFT.BLACK, sysfont, 1.1, nowrap=False)
    _TFT.text((2, 10), "Node:" + NODE_TYPE, TFT.BLACK, sysfont, 1.1, nowrap=False)


def update_display():
    global _TFT, flow_dict
    while True:
        # Flush dynamic part of screen
        _TFT.fillrect((0, 50), (128, 160), TFT.GRAY)
        if flow_dict['current']['water_pump_signal']:
            _TFT.fillrect((110, 50), (20, 10), TFT.GREEN)
            _TFT.text((2, 50), "Water pump on", TFT.BLACK, sysfont, 1.1, nowrap=False)
        else:
            _TFT.fillrect((110, 50), (20, 10), TFT.RED)
            _TFT.text((2, 50), "Water pump off", TFT.BLACK, sysfont, 1.1, nowrap=False)

        if flow_dict['current']['nutrient_pump_signal']:
            _TFT.fillrect((110, 60), (20, 10), TFT.GREEN)
            _TFT.text((2, 60), "Nutr. pump on", TFT.BLACK, sysfont, 1.1, nowrap=False)
        else:
            _TFT.fillrect((110, 60), (20, 10), TFT.RED)
            _TFT.text((2, 60), "Nutr. pump off", TFT.BLACK, sysfont, 1.1, nowrap=False)

        if flow_dict['current']['ph_downer_pump_signal']:
            _TFT.fillrect((110, 70), (20, 10), TFT.GREEN)
            _TFT.text((2, 70), "pH pump on", TFT.BLACK, sysfont, 1.1, nowrap=False)
        else:
            _TFT.fillrect((110, 70), (20, 10), TFT.RED)
            _TFT.text((2, 70), "pH pump off", TFT.BLACK, sysfont, 1.1, nowrap=False)

        _TFT.text((2, 80), "Water Level:" + str(flow_dict['sensors']['water_level']) + "%",
                  TFT.BLACK, sysfont, 1.1, nowrap=False)
        _TFT.text((2, 90), "pH:" + str(flow_dict['sensors']['ph']), TFT.BLACK, sysfont, 1.1, nowrap=False)
        _TFT.text((2, 100), "EC:" + str(flow_dict['sensors']['ec']) + "mS/m", TFT.BLACK, sysfont, 1.1, nowrap=False)
        _TFT.text((2, 110), "ORP:" + str(flow_dict['sensors']['orp']) + "mV", TFT.BLACK, sysfont, 1.1, nowrap=False)
        if flow_dict['soft_fuse']:
            _TFT.text((2, 120), "Soft fuse !", TFT.RED, sysfont, 1.1, nowrap=False)
        _TFT.text((2, 150), __water_firmware_version__,
                  TFT.BLACK, sysfont, 1.1, nowrap=False)
        gc.collect()


def soft_fuse():
    global flow_dict
    while True:
        if (time.time() - flow_dict['updated_at']) > 1:
            water_pump_relay.value(False)
            nutrient_pump_relay.value(False)
            ph_downer_pump_relay.value(False)
            flow_dict['current']['water_pump_signal'] = False
            flow_dict['current']['nutrient_pump_signal'] = False
            flow_dict['current']['ph_downer_pump_signal'] = False
            flow_dict['soft_fuse'] = True
        else:
            flow_dict['soft_fuse'] = False


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
