"""
Connect to wifi + print to tft screen booting message
Author: Shanmugathas Vigneswaran
email: shanmugathas.vigneswaran@outlook.fr
"""
import network
from settings import WIFI_SSID, WIFI_PASSWORD, tft
from utils import boot_display


def connect_access_point():
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect(WIFI_SSID, WIFI_PASSWORD)
        while not sta_if.isconnected():
            boot_display(tft)
    print('network config:', sta_if.ifconfig())


if __name__ == '__main__':
    connect_access_point()
