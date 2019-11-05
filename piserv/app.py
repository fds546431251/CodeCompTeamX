# Flask imports
from flask import Flask, render_template, session, request, redirect, url_for, jsonify, send_file, Response
import json
import graphing as g
import sensors as s

# Initiate app, constants and set Seaborn (to make nicer graphs)
app = Flask(__name__)
DB_LOC = "mongodb://localhost:27017"

@app.route("/")
def index():
    return Response("Sorry, not found.", status=404, mimetype="text/html")


# Example test URl:
# http://localhost:5000/heatmap/temperature
@app.route("/heatmap/<string:sensor_type>")
def heatmap_endpoint(sensor_type):

    heatmap_results = g.heatMap(sensor_type)

    if(type(heatmap_results) == str):
        # Not found/not enough data in database - 500 Error repsonse.
        return Response('{"error": "There was an error with the database. See traceback.", "traceback":' + json.dumps(heatmap_results) + '}', status=500, mimetype="application/json")
    
    elif type(heatmap_results) == float:
        # Successful - Plot and send
        return send_file(f"images/{ heatmap_results }.png", mimetype='image/gif')

    else:
        return Response('{"error", "Sorry, something went wrong."}', status=500, mimetype="application/json")


@app.route('/solenoid/toggle')
def toggle_solenoid():
    # Get solenoid
    global solenoid
    # Toggle solenoid
    solenoid.toggle()
    # Add current state to the database
    s.addDatabaseEntry(solenoid.state, 'solenoid')
    return Response(status=200)


# Example test URl:
# http://localhost:5000/graph/PLACEHOLDER/100000/temperature
@app.route("/graph/<string:dest_ip>/<int:time_period>/<string:sensor_type>")
def graph_endpoint(dest_ip, time_period, sensor_type):
    #TODO: URL decode destination IP in place of PLACEHOLDER
    # For now, hardcode:
    dest_ip = "192.168.0.10"
    # Get data from db
    query_result = g.dbQuery(DB_LOC, dest_ip, time_period, sensor_type)
    
    if(type(query_result) == str):
        # Not found/not enough data in database - 500 Error repsonse.
        return Response('{"error": "There was an error with the database. See traceback.", "traceback":' + json.dumps(query_result) + '}', status=500, mimetype="application/json")
    
    elif type(query_result) == list:
        # Successful - Plot and send
        saved_time = g.graphFunc(query_result, sensor_type)
        return send_file(f"images/{ saved_time }.png", mimetype='image/gif')
    
    else:
        return Response('{"error", "Sorry, something went wrong."}', status=500, mimetype="application/json")

if(__name__ == "__main__"):
    # Instantiate solenoid
    solenoid = s.Solenoid()
    # Disable debug for prod
    app.run(debug=True)