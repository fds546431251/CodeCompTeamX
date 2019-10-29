# Flask imports
from flask import Flask, render_template, session, request, redirect, url_for, jsonify, send_file, Response
import json
import graphing as g

# Initiate app, constants and set Seaborn (to make nicer graphs)
app = Flask(__name__)
DB_LOC = "mongodb://localhost:27017"

# Example test URl:
# http://localhost:5000/graph/Bsf/10000/H

@app.route("/")
def index():
    return Response("Sorry, not found.", status=404, mimetype="text/html")

@app.route("/graph/<string:location>/<int:time>/<string:sensor_type>")
def graph_endpoint(location, time, sensor_type):
    # Get data from db
    query_result = g.dbQuery(DB_LOC, location, time, sensor_type)
    
    if(type(query_result) == str):
        # Not found/not enough data in database - 500 Error repsonse.
        return Response('{"error": "Not enough data found - Need 2 or more points for graph.", "traceback":' + json.dumps(query_result) + '}', status=500, mimetype="application/json")
    
    elif type(query_result) == list:
        # Successful - Plot and send
        saved_time = g.graphFunc(query_result, sensor_type)
        return send_file(f"images/{ saved_time }.png", mimetype='image/gif')
    
    else:
        return Response('{"error", "Sorry, something went wrong."}', status=500, mimetype="application/json")

if(__name__ == "__main__"):
    # Disable debug for prod
    app.run(debug=True)