import pymongo
from datetime import datetime
from hashlib import md5
import gpiozero
import subprocess
# Import Pi specfic modules
try:
    import Adafruit_DHT 
except ImportError as e:
    print("Could not load Adafruit_DHT. Make sure it is installed if running on Pi")
    pass

# Constants
DB_IP = "127.0.0.1"
DEFAULT_SITE = "HQ"
DEFAULT_STATE = 0
OPEN_STATE = 1


class Solenoid():
    """
    Uses the DigitalOutputDevice class from Raspbian gpiozero.
    Call Solenoid.on() to turn on and Solenoid.off() to turn off.
    toggle() will toggle from whatever state it is currently in.
    update() adds a database entry with the new state.
    """
    def __init__(self, pin):
        self._closed = True
        self._interface = gpiozero.DigitalOutputDevice(pin)

    @property
    def closed(self):
        return not self._interface.value

    def close(self):
        self._interface.off()
        self._closed = True
        self.update()

    def open(self):
        self._interface.on()
        self._closed = False
        self.update()

    def update(self):
        addDatabaseEntry(self._interface.value, 'solenoid')

    def toggle(self):
        if self._closed:
            self.open()

        else:
            self.close()

class Scarecrow():
    """
    Uses the DigitalOutputDevice class from Raspbian gpiozero.
    Call Scarecrow.scare() to turn on and Scarecrow.stop_scaring() to turn off.
    toggle() will toggle from whatever state it is currently in.
    update() adds a database entry with the new state.
    """
    def __init__(self, pin):
        self._scaring = False
        self._interface = gpiozero.DigitalOutputDevice(pin)

    @property
    def scaring(self):
        return self.value

    def reset(self):
        self._scaring = False
        self._interface.off()
        self.update()

    def update(self):
        addDatabaseEntry(self._interface.value, 'scarecrow')

    def on(self):
        self._interface.on()
        self._scaring = True
        self.update()

    def off(self):
        self._interface.off()
        self._scaring = False
        self.update()

    def toggle(self):
        if self._scaring:
            self.off()

        else:
            self.on()

def getMyIP():
    """
    Function to return the private IP address of the current device

    Returns:
    :ip str: String IP address (e.g. '192.168.0.1')
    """
    ip = subprocess.check_output("hostname -I", shell=True).decode()
    return ip.split()[0]

def getReading(pin, sensor_type=None):
    """
    Function that polls connected DHT11 sensor and gets the appropriate reading.
    Quite laggy - probably best to periodically poll and cache.

    Params:
    :sensor_type str: String representing the type of reading to take (e.g. 'temperature')

    Returns:
    :reading dict/float: If sensor_type given, float value of reading. If sensor_type not given,
        dictionary of both humidity and temperature readings 
    """
    reading = {"humidity": None, "temperature": None}

    try:
        Adafruit_DHT
    except NameError:
        return {"temperature": 19.0, "humidity": 80.0}

    if sensor_type != None:
        while reading[sensor_type] is None:
            humidity, temperature = Adafruit_DHT.read_retry(11, pin)
            reading["humidity"] = humidity
            reading["temperature"] = temperature
        return reading[sensor_type]
    
    else:
        while reading["temperature"] is None and reading["humidity"] is None:
            humidity, temperature = Adafruit_DHT.read_retry(11, pin)
            reading["humidity"] = humidity
            reading["temperature"] = temperature
        return reading
        

def addDatabaseEntry(value, sensor_type, db_ip=DB_IP):
    """
    Given a value and a sensor type, append the appropriate entry to the database

    Params:
    :value float: Value to be added to the database
    :sensor_type str: String representing the type of reading to add (e.g. 'temperature')

    Returns:
    :None:
    """
    # Connect to db
    myclient = pymongo.MongoClient(f"mongodb://{db_ip}:27017")
    mydb = myclient.sensordata
    # Get current timestamp and construct ID MD5 hash
    rightnow = datetime.timestamp(datetime.now())
    ip = getMyIP()
    id_hash = md5((ip + str(rightnow) + DEFAULT_SITE + str(value)).encode()).hexdigest()
    # Construct the DB entry
    entry = {
        "ip_address": getMyIP(),
        "site": DEFAULT_SITE,
        "time": rightnow,
        "value": value,
        "id": id_hash,
    }
    # Add to the appropriate collection
    mycollection = mydb[sensor_type]
    mycollection.insert_one(entry)
    # Close the db connection
    myclient.close()

if __name__ == "__main__":
    print("I think you meant to run app.py")
