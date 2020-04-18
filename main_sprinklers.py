import gc
import random
from boot import SSID
from sysfont import sysfont
from ST7735 import TFT
from machine import SPI, Pin
from pk import PlantKeeper
import node_type

NODE_TYPE = node_type.SPRINKLER
SPRINKLER_TAG = 'orchid'
PK_API_GATEWAY_HOST = '10.3.141.1'
PK_API_GATEWAY_PORT = 8001

spi = SPI(
    2,
    baudrate=20000000,
    polarity=0,
    phase=0,
    sck=Pin(14),
    mosi=Pin(13),
    miso=Pin(12)
)
tft = TFT(spi, 16, 17, 18)
tft.initb2()
tft.rgb(True)
tft.fill(TFT.BLACK)
tft.fillrect((0, 0), (128, 50), TFT.WHITE)
tft.fillrect((0, 50), (128, 160), TFT.GREEN)
tft.text((2, 2), "Wifi: " + SSID, TFT.BLACK, sysfont, 1.1, nowrap=False)
tft.text((2, 10), "Api Gateway:", TFT.BLACK, sysfont, 1.1, nowrap=False)
tft.text((2, 20), PK_API_GATEWAY_HOST + ":" + str(PK_API_GATEWAY_PORT), TFT.BLACK, sysfont, 1.1, nowrap=False)
tft.text((2, 30), "NodeType:", TFT.BLACK, sysfont, 1.1, nowrap=False)
tft.text((2, 40), NODE_TYPE, TFT.BLACK, sysfont, 1.1, nowrap=False)
tft.text((2, 50), "Tag: " + SPRINKLER_TAG, TFT.BLACK, sysfont, 1.1, nowrap=False)

pk = PlantKeeper(
    host=PK_API_GATEWAY_HOST,
    port=PK_API_GATEWAY_PORT
)
pk.set_node_type(node_type=NODE_TYPE)

if __name__ == '__main__':
    while True:
        sensor = random.randint(10, 30)
        pk.post({"soil_humidity": sensor, 'tag': SPRINKLER_TAG})
        print(pk.power)
        gc.collect()
