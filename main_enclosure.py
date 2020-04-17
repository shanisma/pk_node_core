"""
Example Node Enclosure based on ESP32
Author : Shanmugathas Vigneswaran
email: shanmugathas.vigneswaran@outlook.fr
"""
import gc
import dht
from machine import Pin
from pk import PlantKeeper
import node_type

sensor = dht.DHT11(Pin(14))
pk = PlantKeeper(host='10.3.141.1', port=8001)
pk.set_node_type(node_type=node_type.ENCLOSURE)

if __name__ == '__main__':
    while True:
        try:
            sensor.measure()
            pk.post(
                {
                    "temperature": sensor.temperature(),
                    "humidity": sensor.humidity(),
                    "uv_index": "",
                    'co2_ppm': 0,
                    'cov_ppm': 0
                }
            )
            print(pk.json)
        except KeyboardInterrupt:
            pass
        except OSError:
            pass
        gc.collect()
