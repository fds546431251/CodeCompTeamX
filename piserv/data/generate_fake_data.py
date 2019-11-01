import pymongo
import numpy
from datetime import datetime
import random
from hashlib import md5

ip_addresses = ["192.168.0.10", "192.168.0.20", "192.168.0.30", "192.168.0.40", "192.168.0.50"]
SITE = "HQ"

#################################################################################################
# This script is used to create a database with the appropriate structure and fill it with test
# data. The document syntax can be found in the docstring of the createEntry function
#################################################################################################

def createEntry():
    """
    Create a database entry. Needs to include:
        IP Address - One from the ip_addresses list
        Site - Always HQ for this example
        Time - POSIX timestamp from the last month
        Value - Random entry between 0-100
        ID - MD5 sum of IP+Time+Site+Value
    """
    entry = {}
    entry["ip_address"] = random.choice(ip_addresses)
    entry["site"] = SITE
    entry["time"] = random.randrange(1567296000, int(datetime.timestamp(datetime.now())), 1)
    entry["value"] = random.randrange(0, 101, 1)
    entry["id"] = md5((entry["ip_address"] + str(entry["time"]) + entry["site"] + str(entry["value"])).encode()).hexdigest()
    return entry


myclient = pymongo.MongoClient("mongodb://localhost:27017")
mydb = myclient.sensordata

tables = ["temperature", "humidity", "pressure", "moisture"]

for table in tables:
    mycollection = mydb[table]
    for i in range(10000):
        entry = createEntry()
        mycollection.insert_one(entry)

    
