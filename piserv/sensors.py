import Adafruit_DHT

def getReading(sensor_type):
    """
    Function that polls connected DHT11 sensor and gets the appropriate reading.
    Quite laggy - probably best to periodically poll and cache.

    Params:
    :sensor_type str: String representing the type of reading to take (e.g. 'temperature')
    """
    reading = {"humidity": None, "temperature": None}

    while reading[sensor_type] is None:
        humidity, temperature = Adafruit_DHT.read_retry(11, 4)
        reading["humidity"] = humidity
        reading["temperature"] = temperature

    return reading[sensor_type]