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


def read_sensors():
    return ujson.dumps({"humidity_level": random.randint(0, 100)})


def controller_callback(topic, msg):
    """
    Handle new message coming from the controller
    :param topic:
    :param msg:
    :return:
    """
    print("message received")
    print((topic, msg))


def subscribe_controller():
    sub_client = MQTTClient(NODE_TYPE + "_" + NODE_TAG + "_" + "SUB", SERVER, PORT)
    sub_client.set_callback(controller_callback)
    sub_client.connect()
    sub_client.subscribe(_CONTROLLER_TOPIC)
    while True:
        sub_client.wait_msg()


def publish_sensors():
    pub_client = MQTTClient(NODE_TYPE + "_" + NODE_TAG + "_" + "PUB", SERVER, PORT)
    pub_client.connect()
    while True:
        pub_client.publish(_SENSOR_TOPIC, read_sensors())


_thread.start_new_thread(publish_sensors, ())
_thread.start_new_thread(subscribe_controller, ())
