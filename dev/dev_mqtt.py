import _thread
from umqtt.robust import MQTTClient
import random
import ujson

SERVER = "af120153-db6a-4fdd-a81b-6d902b00e936.nodes.k8s.fr-par.scw.cloud"
PORT = 32500
NODE_TYPE = "sprinkler"
NODE_TAG = 'orchid'

_SENSOR_TOPIC = NODE_TYPE + "/" + NODE_TAG + "/" + "sensor"
_CONTROLLER_TOPIC = NODE_TYPE + "/" + NODE_TAG + "/" + "controller"

_REGISTRY_SIGN_TOPIC = 'sprinkler/config/registry'
_REGISTRY_VALIDATION_TOPIC = "sprinkler/config/registry/validation/" + NODE_TAG

registered = False


def register():
    c = MQTTClient(NODE_TYPE + "_" + NODE_TAG + "_" + "REGISTRY ", SERVER, PORT)
    c.connect()
    c.publish(_REGISTRY_SIGN_TOPIC, ujson.dumps({"tag": NODE_TAG}))


def wait_registry_response():
    global registered

    def callback(topic, msg):
        global registered
        registered = ujson.loads(msg)['acknowledge']
        raise ValueError('force close subscription')

    c = MQTTClient(NODE_TYPE + "_" + NODE_TAG + "_" + "SUB", SERVER, PORT)
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
        print((topic, msg))

    c = MQTTClient(NODE_TYPE + "_" + NODE_TAG + "_" + "SUB", SERVER, PORT)
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

    c = MQTTClient(NODE_TYPE + "_" + NODE_TAG + "_" + "PUB", SERVER, PORT)
    c.connect()
    while True:
        c.publish(_SENSOR_TOPIC, read_sensors())


# =================================
# Register tag to Master
# =================================
register()
try:
    wait_registry_response()
except ValueError:
    pass
print(registered)

# =================================
# Subscription to controller
# =================================
_thread.start_new_thread(subscribe_controller, ())

# =================================
# Subscription to controller
# =================================
_thread.start_new_thread(publish_sensors, ())
