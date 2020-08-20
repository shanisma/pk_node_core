"""
Node Type Sprinkler I/O function and configuration
Author: Shanmugathas Vigneswaran
Email: shanmugathas.vigneswaran@outlooK.fr
"""

from machine import Pin, ADC
from utils import fit
from influxdb_line_protocol import Metric

# ======================== Input  =========================
# =========================================================
soi_moisture_sensor = ADC(Pin(34))
soi_moisture_sensor.atten(ADC.ATTN_11DB)
# Use soil_moisture_map to transform
# ADC to percent of water level
soil_moisture_map = fit(
    # Map analog read min/max
    [2330, 1390],
    # to 0% to 100%
    [0, 100]
)


def read_sensors(tag):
    soil_moisture_raw_adc = soi_moisture_sensor.read()
    soil_moisture = soil_moisture_map(soil_moisture_raw_adc)

    # builtin round function seem not working
    # https://forum.micropython.org/viewtopic.php?t=802
    # soil_moisture = round(soil_moisture, 2)
    soil_moisture = int(soil_moisture)
    if soil_moisture < 0:
        soil_moisture = 0
    elif soil_moisture > 100:
        soil_moisture = 100

    metric = Metric("sprinkler")
    metric.add_tag('tag', tag)
    metric.add_value('soil_moisture_raw_adc', soil_moisture_raw_adc)
    metric.add_value('soil_moisture', soil_moisture)

    return {
        "tag": tag,
        "soil_moisture_raw_adc": soil_moisture_raw_adc,
        "soil_moisture": soil_moisture,
        "influx_message": str(metric)
    }


# ======================== Output  ========================
# =========================================================
water_valve_relay = Pin(19, Pin.OUT)
