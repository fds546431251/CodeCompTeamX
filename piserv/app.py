from flask import Flask, render_template, session, request, redirect, url_for, jsonify, send_file
import json
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sb
import os
import pymongo

# Initiate app and set Seaborn (to make nicer graphs)
app = Flask(__name__)
sb.set()

#TODO: Function that sets up the test MongoDB

def dbQuery(location, time, sensor_type):
    """
    Takes in location (e.g. carrot patch), time (how far back in time to get data for) and sensor type (T, H etc.)
    and returns the data from the database that match these criteria - for plotting
    
    Params:
    :location string: Location of desired sensor (e.g 'Bsf')
    :time int: Number of seconds back to look (for use with UTC codes)
    :sensor_type char: Character depicting type of value (Temperature, Humidity etc.)

    Returns:
    :data - np.array: Array of tuples of (timestamp, value)
    """

    myclient = pymongo.MongoClient("mongodb://localhost:27017")
    mydb = myclient.GARDEN
    mycollection = mydb.BENHALL

    query = {
        "site": location,
        "type": sensor_type,
        # Regex - starting with "2" just for now - will need to be $gt a value...
        "timestamp": { "$regex" : "^2"}
    }

    results = mycollection.find(query)
    # Only return timestamp and values
    data = [(x["timestamp"], x["value"]) for x in results]
    
    myclient.close()
    return data

def graphFunc(data, sensor_type):
    """
    Takes in an array of data (as returned from dbQuery()) and the sensor type.
    Produces corresponding graph and returns the exact POSIX timestamp that the figure was created.
    This timestamp is also what the figure is saved as

    Params:
    :data np.array: Array of data as returned from dbQuery() (Array of tuples)
    :sensor_type char: Character representing sensor type (e.g. 'T' for temperature)
    """
    # Convert sensor_type into friendly name for Y axis label
    if(sensor_type == "T"):
        friendly_type = "Temperature (C)"
    elif(sensor_type == "H"):
        friendly_type = "Humidity"
    else:
        friendly_type = "$CO_2$"

    # Risky but probably needed - Means only 1 image is ever stored
    os.system("rm -f images/*")

    # Line plot
    x = [i[0] for i in data]
    y = [i[1] for i in data]
    plt.cla()
    plt.plot(x, y)
    # Label axes, title and set ticks to correct orientation
    plt.title(f"Graph showing { friendly_type } against Time.")
    plt.xlabel("Time")
    plt.ylabel(f"{ friendly_type }")
    plt.xticks(rotation=50)
    # Ensure spacing at bottom of image
    fig = plt.gcf()
    fig.subplots_adjust(bottom=0.22)
    # Get POSIX timestamp and save image
    rightnow = datetime.timestamp(datetime.now())
    plt.savefig(f"images/{ rightnow }.png")
    return rightnow

@app.route("/")
def index():
    return "Hello, world!"

@app.route("/graph/<string:location>/<int:time>/<string:sensor_type>")
def graph_endpoint(location, time, sensor_type):
    # Get data from db
    data = dbQuery(location, time, sensor_type)
    # Plot figure and save
    saved_time = graphFunc(data, sensor_type)
    # Send image back to browser
    return send_file(f"images/{ saved_time }.png", mimetype='image/gif')

if(__name__ == "__main__"):
    # Disable debug for prod
    app.run(debug=True)