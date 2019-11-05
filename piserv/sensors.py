import pymongo
from datetime import datetime
from hashlib import md5
import subprocess
# Import Pi specfic modules
try:
    import Adafruit_DHT 
except ImportError as e:
    print("Could not load Adafruit_DHT. Make sure it is installed if running on Pi")
    pass

# Constants
DB_IP = "192.168.0.10"
DEFAULT_SITE = "HQ"
DEFAULT_STATE = 0
OPEN_STATE = 1

class Solenoid():
    def __init__(self):
        self._closed = True
        self.state = DEFAULT_STATE
        # Update this bit to not use PiFaceDigital when using a different relay...
        self.interface = pfd.PiFaceDigital().relays[0]
        self.interface.turn_off()

    @property
    def closed(self):
        return self._closed

    def toggle(self):
        if self._closed:
            self._closed = False
            self.state = OPEN_STATE
            self.interface.turn_on()
        else:
            self._closed = True
            self.state = DEFAULT_STATE
            self.interface.turn_off()

    
# def toggleSolenoid():
#     """
#     USE THE CLASS INSTEAD
#     Toggles the solenoid connected to PiFace Digital relay and returns the current state.
#     Additionally adds a database entry for tracking the solenoid activation.

#     Returns:
#     :state int: Integer representing the current state of the solenoid (1 for open, 0 for closed)
#     """
#     piface = pfd.PiFaceDigital()
#     piface.relays[0].turn_on()
#     return

def getMyIP():
    """
    Function to return the private IP address of the current device

    Returns:
    :ip str: String IP address (e.g. '192.168.0.1')
    """
    ip = subprocess.check_output("hostname -I", shell=True).decode()
    return ip.split()[0]

def getReading(sensor_type=None):
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

    if sensor_type != None:
        while reading[sensor_type] is None:
            humidity, temperature = Adafruit_DHT.read_retry(11, 4)
            reading["humidity"] = humidity
            reading["temperature"] = temperature
        return reading[sensor_type]
    
    else:
        while reading["temperature"] is None and reading["humidity"] is None:
            humidity, temperature = Adafruit_DHT.read_retry(11, 4)
            reading["humidity"] = humidity
            reading["temperature"] = temperature
        return reading
        

def addDatabaseEntry(value, sensor_type):
    """
    Given a value and a sensor type, append the appropriate entry to the database

    Params:
    :value float: Value to be added to the database
    :sensor_type str: String representing the type of reading to add (e.g. 'temperature')

    Returns:
    :None:
    """
    # Connect to db
    myclient = pymongo.MongoClient(f"mongodb://{DB_IP}:27017")
    mydb = myclient.sensordata
    # Get current timestamp and construct ID MD5 hash
    rightnow = datetime.timestamp(datetime.now())
    id_hash = md5((getMyIP + str(rightnow) + DEFAULT_SITE + str(value)).encode()).hexdigest()
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
    addDatabaseEntry()
