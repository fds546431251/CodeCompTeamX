# Basic flask app - to be expanded in order to interface with AWS and local Pis

from flask import Flask, make_response, jsonify, request
import json
from hashlib import md5
app = Flask(__name__)

#==============================================================================================
# Constants and Data
#==============================================================================================
# Example device class and devices list - this should be a DB:
class Device(object):
    """
    Class to look after devices. Initiated with friendly name, IP address and accepted methods.
    Some helper functions built in.
    """
    def __init__(self, friendly, address, methods):
        self.address  = address
        self.name = md5(friendly.encode()).hexdigest()
        self.methods = methods
        self.friendly = friendly

    def updateAddress(self, newAddr):
        # TODO: Update address function
        return

    def updateName(self, newName):
        self.name = md5(newName.encode()).hexdigest()
        return

    def jsonConstructor(self):
        value = {
            "addr": self.address,
            "methods": self.methods
        }
        key = self.name

        return key, value

DEVICES_Classes = [
    Device("carrot patch", "127.0.0.1:9090", ["GET", "POST"]),
    Device("front lawn", "127.0.0.1:8080", ["GET", "POST"]),
    Device("duck pond", "127.0.0.1:1010", ["Get"])
]

DEVICES = {
    obj.jsonConstructor()[0]: obj.jsonConstructor()[1] for obj in DEVICES_Classes
}

# Accepted services:
ACCEPTED_SERVICES = [
    "temp",
    "pic",
    "move"
]

#==============================================================================================
# AWS Side

#- GET method for a specific device - returns data reading for whichever device is accessed.
#-- Take in a DEVICE_FRIENDLY_NAME and find the corresponding UID (or local IP)
#-- Perform a request to the relevant IP in order to get data.
#-- Get the response from the local device and return from API

#- POST method for a specific device (e.g. Actuator) - Perform action and return 200 OK.
#-- Take in DEVICE_FRIENDLY_NAME and find the corresponding device
#-- Perform a request to the relevant IP in order to perform action
#-- Update saved device state (to keep track of state e.g. can't turn off something that's
#   already off)
#-- If action is not valid, return 400 with error data
#-- If action is successful, return 200 OK
#==============================================================================================

@app.route('/', methods=['GET'])
def hello_world():
    """
    Default route for when the API is accessed without an endpoint e.g. through a browser.
    Return a 403 forbidden by default.
    """
    return make_response("<html><h1>403 Forbidden</h1>\n<h2>Sorry, you do not have permission to access this page.</h2></html>", 403)

@app.route('/api/device/<string:dev_uid>/<string:service>', methods=['GET', 'POST'])
def get_device(dev_uid, service):
    """
    Takes in the device UID as sent from AWS.
    Determines whether the request method is available for the device.
    Performs the appropriate request to the appropriate device.

    :param dev_uid: Device UID as passed into URL.
    """

    # Check that device is registered
    if dev_uid not in DEVICES:
        return make_response(jsonify({"error": "Device not found"}), 404)

    # Check that request method is valid
    elif request.method not in DEVICES[dev_uid]["methods"]:
        return make_response(jsonify({"error": "Request type not valid", "methods":DEVICES[dev_uid]["methods"], "req_method":request.method}), 400)
    
    # Check to see if the service is accepted
    elif service not in ACCEPTED_SERVICES:
        # TODO: Make this bespoke to each device
        return make_response(jsonify({"error":"Service not supported."}), 400)

    # All else valid, return the result
    else:
        # TODO: Poll local devices
        return make_response(jsonify({"device": DEVICES[dev_uid], "service": service}), 200)

#==============================================================================================
## Pi Side
#==============================================================================================
# TODO: Implement Pi-side functions in order to interface with local devices

def requestReading(device):
    return

if(__name__ == "__main__"):
    app.run()