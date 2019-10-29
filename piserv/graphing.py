import pymongo
from datetime import datetime
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as dates
import traceback
import seaborn as sb
sb.set()

# Constants
SCREEN_HEIGHT = 600.
SCREEN_WIDTH = 1024.
FONT_SIZE= 11

def dbQuery(db_ip, location, time, sensor_type):
    """
    Takes in database link, location (e.g. carrot patch), time (how far back in time to get data for) and sensor type (T, H etc.)
    and returns the data from the database that match these criteria - for plotting
    
    Params:
    :db_ip string: Location of database (protocol + ip + port)
    :location string: Location of desired sensor (e.g 'Bsf')
    :time int: Number of seconds back to look (for use with UTC codes)
    :sensor_type char: Character depicting type of value (Temperature, Humidity etc.)

    Returns:
    :data - lis: List of tuples of (timestamp, value)
    """
    myclient = pymongo.MongoClient(db_ip)
    mydb = myclient.GARDEN
    mycollection = mydb.BENHALL

    return_val = None
    
    query = {
        "site": location,
        "type": sensor_type,
        "timestamp": { "$gt" : datetime.timestamp(datetime.now()) - time}
    }
    
    try:
        results = mycollection.find(query)
        results_list = [x for x in results]
        results_length = len(results_list)
        assert results_length > 1
    
    except AssertionError as e:
        print("[dbQuery] Not enough data found - Need 2 or more points")
        return_val = traceback.format_exc()
    
    else:
        # Only return timestamp and values
        print("[dbQuery] Data found.")
        data = [(x["timestamp"], x["value"]) for x in results_list]
        data = sorted(data, key=lambda x: x[0])
        return_val = data
    
    finally:
        print("[dbQuery] Returning response")
        myclient.close()
        return return_val

def graphFunc(data, sensor_type):
    """
    Takes in an array of data (as returned from dbQuery()) and the sensor type.
    Produces corresponding graph and returns the exact POSIX timestamp that the figure was created.
    This timestamp is also what the figure is saved as

    Params:
    :data list: List of data as returned from dbQuery() (List of tuples)
    :sensor_type char: Character representing sensor type (e.g. 'T' for temperature)
    """
    # Convert sensor_type into friendly name for Y axis label
    # TODO: Make sure all options are covered here:
    if(sensor_type == "T"):
        friendly_type = "Temperature ($^{\circ}$C)"
    elif(sensor_type == "H"):
        friendly_type = "Humidity"
    elif(sensor_type == "C"):
        friendly_type = "$CO_2$"
    else:
        friendly_type = ""

    # Risky but probably needed - Means only 1 image is ever stored.
    # Could save all images without a problem but would quickly take up space.
    # Just comment out to remove
    os.system("rm -f images/*")

    # Get data sets
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
        tick.label.set_fontname('Arial')
        tick.label.set_fontsize(FONT_SIZE)

    ax.plot_date(date, y, '-x')

    # Label axes, title and set ticks to correct orientation
    plt.title(f"Graph showing { friendly_type } against Time.")
    plt.xlabel("Date & Time")
    plt.ylabel(f"{ friendly_type }")

    # Set time axis ticks to look nice
    ax.xaxis.set_minor_locator(dates.HourLocator(interval=4))   # every 4 hours
    ax.xaxis.set_minor_formatter(dates.DateFormatter('%H:%M'))  # hours and minutes
    ax.xaxis.set_major_locator(dates.DayLocator(interval=1))    # every day
    ax.xaxis.set_major_formatter(dates.DateFormatter('\n%d-%m-%Y'))
    fig.autofmt_xdate()

    # Ensure spacing at bottom and left of image
    
    fig = plt.gcf()
    plt.grid(True)
    #fig.subplots_adjust(bottom=0.25, left=0.2)

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