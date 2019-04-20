from flask import Flask, jsonify
# Jupyter notebooks should not be used in flask applications
# per Cam on 4/13

# imports mostly same as in notebook
import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

engine = create_engine("sqlite:///Resources/hawaii.sqlite",connect_args={'check_same_thread': False})
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

# continue to copy the important stuff over from the notebook:

# Calculate the date 1 year ago from the last data point in the database
latest_date, = session.query(Measurement.date).order_by(Measurement.date.desc()).first() 
print("Latest Date in database:  " + latest_date)
last_year = str(int(latest_date[0:4])-1)
latest_minus_year = last_year + latest_date[4:11]
print("One Year Prior To Latest: " + latest_minus_year)

# Perform a query to retrieve the data and precipitation scores
precip_data = list(session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date>=latest_minus_year))

#  save the query results as a dictionary
precip_data = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date>=latest_minus_year)
precip_dict = []
for i in precip_data:
    precip_dict.append({"date":i[0], "amount":i[1]})

# we will also need a list of stations...
station_data = list(session.query(Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation))
station_dict = []
for i in station_data:
    station_dict.append({"station":i[0],"name":i[1],"latitude":i[2],"longitude":i[3],"elevation":i[4]})

# ... and temperatures...
temp_data = list(session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.date>=latest_minus_year))
temp_dict = []
for i in temp_data:
    temp_dict.append({"date":i[0], "tobs":i[1]})

# Finally, we will need this function copied over and slightly modified...
#
# This function called `calc_temps` will accept start date and end date in the format '%Y-%m-%d' 
# and return the minimum, average, and maximum temperatures for that range of dates
def calc_temps(start_date, end_date=latest_date):
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    
    return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()


#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    return (
        f"Welcome to the Hawaiian Weather API!<br/>"
        f"Available Routes:<br/>"
        f"/api/precipitation<br/>"
        f"/api/stations<br/>"
        f"/api/temperature<br/>"
        f"/api/<start date><br/>"
        f"/api/<start date>/<end date><br/>"
    )

@app.route("/api/precipitation")
def precipitation():
    return jsonify(precip_dict)

@app.route("/api/stations")
def stations():
    return jsonify(station_dict)

@app.route("/api/temperature")
def temperature():
    return jsonify(temp_dict)

@app.route("/api/<startdate>")
def daterange1(startdate):
    td_list = calc_temps(startdate)
    td_dict = {"minimum":td_list[0][0], "average":td_list[0][1], "maximum":td_list[0][2]}
    return jsonify(td_dict)

@app.route("/api/<startdate>/<enddate>")
def daterange2(startdate,enddate):
    td_list = calc_temps(startdate,enddate)
    td_dict = {"minimum":td_list[0][0], "average":td_list[0][1], "maximum":td_list[0][2]}
    return jsonify(td_dict)

if __name__ == "__main__":
    app.run(debug=True)
