"""

Plant keeper Water ESP32 firmware
Use:
    - Pin 21 for HCSR04 trigger, 22 for echo, use +5V not +3.3V
    - Pin 26 for Pump activation
    - TFT Screen ST7735 Pins: 4, 2, 23, 18, 15
        tested with supplier = Az Delevery

Author : Shanmugathas Vigneswaran
mail : shangmuathas.vigneswaran@outlook.fr

"""
__version__ = 'wip-no-release'

import gc
import time
from boot import SSID
from sysfont import sysfont
from ST7735 import TFT
from hcsr04 import HCSR04
from machine import SPI, Pin, ADC
from utils import fit
from pk import PlantKeeper
import node_type

# Node and Api Gateway setting
NODE_TYPE = node_type.WATER
PK_API_GATEWAY_HOST = '10.3.141.1'
PK_API_GATEWAY_PORT = 8001
# Soil humidity sensors setting
water_level_sensor = HCSR04(trigger_pin=21, echo_pin=22, echo_timeout_us=10000)
WATER_LEVEL_FIT = fit(
    # Map analog read min/max
    [118, 34],
    # to 0% to 100%
    [0, 100]
)
# Relay for valve power on / power off
PUMP_RELAY = Pin(26, Pin.OUT)

SPI = SPI(
    2, baudrate=20000000,
    polarity=0, phase=0,
    sck=Pin(18), mosi=Pin(23), miso=Pin(12)
)
POWER_COLOR = TFT.GREEN

# Print Node information / Static section
tft = TFT(SPI, 2, 4, 15)
tft.initb2()
tft.rgb(True)
tft.fill(TFT.BLACK)
tft.fillrect((0, 0), (128, 50), TFT.WHITE)
tft.fillrect((0, 50), (128, 160), TFT.RED)
tft.text((2, 2), "Wifi: " + SSID, TFT.BLACK, sysfont, 1.1, nowrap=False)
tft.text((2, 10), "Api Gateway:", TFT.BLACK, sysfont, 1.1, nowrap=False)
tft.text((2, 20), PK_API_GATEWAY_HOST + ":" + str(PK_API_GATEWAY_PORT), TFT.BLACK, sysfont, 1.1, nowrap=False)
tft.text((2, 30), "NodeType:", TFT.BLACK, sysfont, 1.1, nowrap=False)
tft.text((2, 40), NODE_TYPE, TFT.BLACK, sysfont, 1.1, nowrap=False)

# Create Plant Keeper Client
pk = PlantKeeper(
    host=PK_API_GATEWAY_HOST,
    port=PK_API_GATEWAY_PORT
)
pk.set_node_type(node_type=NODE_TYPE)

last_power = False
if __name__ == '__main__':
    while True:
        try:
            raw_distance = water_level_sensor.distance_mm()
            percent = int(WATER_LEVEL_FIT(raw_distance))

            # Post to Api Gateway sensor value
            pk.post({"level": percent})
            # +----------------------------------------------------+
            # | Builtin TFT screen processing (dynamic zone)       |
            # +----------------------------------------------------+
            # full back ground GREEN = Power ON / RED = Power OFF
            if last_power:
                POWER_COLOR = TFT.GREEN
            else:
                POWER_COLOR = TFT.RED
            # Flush dynamic part of screen
            tft.fillrect((0, 50), (128, 160), POWER_COLOR)
            # Print relevant values for user
            tft.text((2, 50), "Raw distance: " + str(raw_distance), TFT.BLACK, sysfont, 1.1, nowrap=False)
            tft.text((2, 60), "% fill: " + str(percent), TFT.BLACK, sysfont, 1.1, nowrap=False)
            tft.text((2, 70), "Power: " + str(pk.power), TFT.BLACK, sysfont, 1.1, nowrap=False)
            # +----------------------------------------------------+
            # | Activate / Deactivate relay                        |
            # +----------------------------------------------------+
            if not last_power:
                last_power = pk.power
                PUMP_RELAY.value(pk.power)
            else:
                if pk.power != last_power:
                    PUMP_RELAY.value(pk.power)
            last_power = pk.power

            gc.collect()
            time.sleep(0.5)
        except Exception as ex:
            PUMP_RELAY.value(0)
            last_power = 0
            tft.text((2, 60), "ERROR ", TFT.BLACK, sysfont, 2, nowrap=False)
            tft.text(
                (2, 80),
                str(ex.__class__.__name__) + ":" + str(ex),
                TFT.BLACK,
                sysfont,
                1.2,
                nowrap=False
            )
            gc.collect()
            time.sleep(2)
