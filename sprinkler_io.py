from machine import Pin, ADC
from utils import fit

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
    return {
        "tag": tag,
        "soil_moisture_raw_adc": soil_moisture_raw_adc,
        "soil_moisture": soil_moisture
    }


# ======================== Output  ========================
# =========================================================
water_valve_relay = Pin(26, Pin.OUT)
