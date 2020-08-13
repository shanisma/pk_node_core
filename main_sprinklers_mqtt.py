import ujson
import random
import _thread
from boot import SSID
from ST7735 import TFT
from sysfont import sysfont
from umqtt.robust import MQTTClient
from settings import tft

NODE_TYPE = "sprinkler"
NODE_TAG = 'orchid'

_SENSOR_TOPIC = NODE_TYPE + "/sensor"
_CONTROLLER_TOPIC = NODE_TYPE + "/controller"

_REGISTRY_SIGN_TOPIC = 'sprinkler/config/registry'
_REGISTRY_VALIDATION_TOPIC = "sprinkler/config/registry/validation/" + NODE_TAG

registered = False
flow_dict = {"last_power": False}


def register():
    c = MQTTClient(
        NODE_TYPE
        + "_"
        + NODE_TAG
        + "_REG",
        MQTT_SERVER,
        MQTT_PORT
    )
    c.connect()
    c.publish(
        _REGISTRY_SIGN_TOPIC,
        ujson.dumps({"tag": NODE_TAG})
    )


def wait_registry_response():
    global registered

    def callback(topic, msg):
        global registered
        registered = ujson.loads(msg)['acknowledge']
        raise ValueError('force close subscription')

    c = MQTTClient(
        NODE_TYPE
        + "_"
        + NODE_TAG
        + "_REG_VALIDATE",
        MQTT_SERVER,
        MQTT_PORT
    )
    c.set_callback(callback)
    c.connect()
    c.subscribe(_REGISTRY_VALIDATION_TOPIC)
    try:
        while True:
            c.wait_msg()
    finally:
        c.disconnect()


def subscribe_controller():
    def callback(topic, msg):
        d = ujson.loads(msg)
        if d['tag'] == NODE_TAG:
            print((topic, msg))

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
    def read_sensors():
        return ujson.dumps(
            {
                "soil_moisture": random.randint(0, 100)
            }
        )

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
        c.publish(_SENSOR_TOPIC, read_sensors())


def init_display(_tft):
    global registered
    wifi_ssid = SSID
    if len(wifi_ssid) >= 14:
        wifi_ssid = SSID[0:14]

    _tft.fill(TFT.BLACK)
    _tft.fillrect((0, 0), (128, 50), TFT.WHITE)
    _tft.fillrect((0, 50), (128, 160), TFT.RED)
    _tft.text((2, 2), "Wifi:" + wifi_ssid, TFT.BLACK, sysfont, 1.1, nowrap=False)
    _tft.text((2, 10), "Node:" + NODE_TYPE, TFT.BLACK, sysfont, 1.1, nowrap=False)
    _tft.text((2, 20), "Tag: " + NODE_TAG, TFT.BLACK, sysfont, 1.1, nowrap=False)
    if not registered:
        _tft.text((2, 30), "WARNING:tag already registered !!!", TFT.BLACK, sysfont, 1.1, nowrap=False)


def update_display(_tft):
    global flow_dict
    if flow_dict['last_power']:
        POWER_COLOR = TFT.GREEN
    else:
        POWER_COLOR = TFT.RED
    # Flush dynamic part of screen
    _tft.fillrect((0, 50), (128, 160), POWER_COLOR)
    # Print relevant values for user
    _tft.text((2, 50), "Tag: " + NODE_TAG, TFT.BLACK, sysfont, 1.1, nowrap=False)
    _tft.text((2, 60), "Raw ADC: ", TFT.BLACK, sysfont, 1.1, nowrap=False)
    _tft.text((2, 70), "Soil humidity: ", TFT.BLACK, sysfont, 1.1, nowrap=False)
    _tft.text((2, 80), "Power: ", TFT.BLACK, sysfont, 1.1, nowrap=False)


# =================================
# Register tag to Master
# =================================
register()
try:
    wait_registry_response()
except ValueError:
    pass
init_display(tft)

# =================================
# Subscription to controller
# =================================
_thread.start_new_thread(subscribe_controller, ())

# =================================
# Subscription to controller
# =================================
_thread.start_new_thread(publish_sensors, ())
