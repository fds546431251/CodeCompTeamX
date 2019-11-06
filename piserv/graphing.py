import pymongo
from datetime import datetime
import os
import numpy as np
import json
import matplotlib.pyplot as plt
import matplotlib.dates as dates
import traceback
import seaborn as sb
sb.set()

# Constants
SCREEN_HEIGHT = 600.
SCREEN_WIDTH = 1024.
FONT_SIZE= 11
ACCEPTED_SENSORS = ["temperature", "humidity", "pressure", "moisture"]
IP_ADDRESSES = ["192.168.0.10", "192.168.0.20", "192.168.0.30", "192.168.0.40", "192.168.0.50"]

def dbQuery(db_ip, slave_ip_address, time_period, sensor_type):
    """
    Takes in database link, location (e.g. carrot patch), time (how far back in time to get data for) and sensor type (T, H etc.)
    and returns the data from the database that match these criteria - for plotting
    
    Params:
    :db_ip string: Location of database (protocol + ip + port)
    :slave_ip_address string: IP address of desired slave Pi (e.g. "192.168.0.24")
    :time_period int: Number of seconds back to look (for use with UTC codes e.g. 1 hour = 3600)
    :sensor_type str: String depicting type of sensor (temperature, humidity etc.)

    Returns:
    :data - list: List of tuples of (timestamp, value)
    """
    # Check sensor is valid
    try:
        assert sensor_type in ACCEPTED_SENSORS
    except AssertionError as e:
        print("[dbQuery] Given sensor type is not valid")
        return traceback.format_exc()
    
    #print(f"[dbQuery] Params: {db_ip}, {slave_ip_address}, {time_period}, {sensor_type}")

    # Instantiate db connection
    myclient = pymongo.MongoClient(db_ip)
    mydb = myclient.sensordata
    mycollection = mydb[sensor_type]

    # Instantiate return value - needed for returning errors
    return_val = None
    
    # Query object for db
    query = {
        "ip_address": slave_ip_address,
        "time": { "$gt" : datetime.timestamp(datetime.now()) - time_period}
    }
    
    #print(f"[dbQuery] Query: {json.dumps(query)}")

    # Find data by query object and ensure there is enough data to plot
    try:
        results = mycollection.find(query)
        results_list = [x for x in results]
        results_length = len(results_list)
        #print(f"[dbQuery] Number of results: {results_length}\nResults:\n{results_list}")

        assert results_length > 1
    
    # If not enough data, error
    except AssertionError as e:
        print("[dbQuery] Not enough data found - Need 2 or more points")
        return_val = traceback.format_exc()
    
    # If okay, return values
    else:
        # Only return timestamp and values
        print("[dbQuery] Data found.")
        results_list = sorted(results_list, key=lambda x: x["time"])
        return_val = [x for x in results_list]
    
    # Return data and close db connection
    finally:
        print("[dbQuery] Returning response")
        myclient.close()
        return return_val

def heatMap(sensor_type, db_ip="mongodb://localhost:27017"):
    """
    Takes in a sensor type to query.
    Produces corresponding heatmap and returns the exact POSIX timestamp when the figure was created.
    The timestamp is also what the figure is saved as.

    Params:
    :sensor_type str: String depicting type of sensor (temperature, humidity etc...)
    :db_ip str: Location of the MongoDB on the network.

    Returns:
    :rightnow int: POSIX timestamp of the time the resultant image was saved - Also the filename.
    """

    try:
        assert sensor_type in ACCEPTED_SENSORS
    except AssertionError as e:
        print("[heatMap] Given sensor type is not valid")
        return traceback.format_exc()

    # Risky but probably needed - Means only 1 image is ever stored.
    # Could save all images without a problem but would quickly take up space.
    # Just comment out to remove
    os.system("rm -f images/*")

    latest = []
    for ip in IP_ADDRESSES:
        data = dbQuery(db_ip, ip, 72000, sensor_type)
        latest.append(data[-1])
    
    #TODO: Make an actual heatmap...
    # Clear current fig
    plt.cla()

    # Set fig dimensions and remove axes
    fig = plt.figure(frameon=False)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis('off')
    DPI = fig.get_dpi()
    fig.set_size_inches(SCREEN_WIDTH/float(DPI),SCREEN_HEIGHT/float(DPI))
    fig.patch.set_visible(False)

    # Plot base image
    im = plt.imread("data/garden_map.png")
    implot = plt.imshow(im)

    # Get current timestamp and save
    rightnow = datetime.timestamp(datetime.now())
    plt.savefig(f"images/{ rightnow }.png")

    return rightnow

def graphFunc(data, sensor_type, time_period):
    """
    Takes in an array of data (as returned from dbQuery()) and the sensor type.
    Produces corresponding graph and returns the exact POSIX timestamp that the figure was created.
    This timestamp is also what the figure is saved as

    Params:
    :data list: List of data as returned from dbQuery() (List of db documents)
    :sensor_type str: String depicting type of sensor (temperature, humidity etc...)
    :time_period float: Float depicting time period to graph over.

    Returns:
    :rightnow int: POSIX timestamp of the time the resultant image was saved - Also the filename.
    """
    # Check sensor type is valid
    try:
        assert sensor_type in ACCEPTED_SENSORS
    except AssertionError as e:
        print("[graphFunc] Given sensor type is not valid")
        return traceback.format_exc()

    # Convert sensor_type into friendly name for Y axis label
    if(sensor_type == "temperature"):
        friendly_type = "Temperature ($^{\circ}$C)"

    elif(sensor_type == "humidity"):
        friendly_type = "Humidity"

    else:
        friendly_type = ""

    # Risky but probably needed - Means only 1 image is ever stored.
    # Could save all images without a problem but would quickly take up space.
    # Just comment out to remove
    os.system("rm -f images/*")

    # Get data sets
    data = [(x["time"], x["value"]) for x in data]
    data = sorted(data, key=lambda x: x[0])
    x = [i[0] for i in data]
    y = [i[1] for i in data]

    # Convert POSIX to dates
    datconv = np.vectorize(datetime.fromtimestamp)
    date = datconv(x)

    # Plot data
    print("[graphFunc] Plotting data.")
    plt.cla()
    fig, ax = plt.subplots()

    # Change font size
    for tick in (ax.xaxis.get_major_ticks()):
        tick.label.set_fontsize(FONT_SIZE)

    ax.plot_date(date, y, '-x')

    # Label axes, title and set ticks to correct orientation
    plt.title(f"Graph showing { friendly_type } against Time.")
    plt.xlabel("Date & Time")
    plt.ylabel(f"{ friendly_type }")

    # Set time axis ticks to look nice
    if time_period < 172800:            # Less than 2 days?
        ax.xaxis.set_minor_locator(dates.HourLocator(interval=4))   # every 4 hours
        ax.xaxis.set_minor_formatter(dates.DateFormatter('%H:%M'))  # hours and minutes
    if time_period < 864000:            # Less than 10 days?
        ax.xaxis.set_major_locator(dates.DayLocator(interval=1))    # every day
        ax.xaxis.set_major_formatter(dates.DateFormatter('\n%d-%m-%Y'))
    else:
        ax.xaxis.set_major_locator(dates.DayLocator(interval=5))    # every 5 days
        ax.xaxis.set_major_formatter(dates.DateFormatter('\n%d-%m-%Y'))
    fig.autofmt_xdate()

    # Ensure spacing at bottom and left of image
    fig = plt.gcf()
    plt.grid(True)
    #fig.subplots_adjust(bottom=0.25, left=0.2)

    # Set picture dimensions to that of Alexa cards
    DPI = fig.get_dpi()
    fig.set_size_inches(SCREEN_WIDTH/float(DPI),SCREEN_HEIGHT/float(DPI))

    # Get current timestamp and save image
    print("[graphFunc] Saving figure.")
    rightnow = datetime.timestamp(datetime.now())
    plt.savefig(f"images/{ rightnow }.png")

    # Return timestamp (used for filename)
    return rightnow        

if(__name__ == "__main__"):
    print("I think you meant to run app.py")