# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
#Reflect database into classes
Base = automap_base()
#Reflect tables
Base.prepare(engine, reflect = True)
#Set variables
measurement = Base.classes.measurement
station = Base.classes.station
# Create our session (link) from Python to the DB
session = Session(engine)
#################################################
# Flask Setup
#################################################

app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
    print("All api routes")
    return (
        f"Available Routes: <br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start (enter with YYYY-MM-DD)<br/>"
        f"/api/v1.0/start/end<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    one_year = dt.date(2017, 8, 23)- dt.timedelta(days= 365)
    prev_year = dt.date(one_year.year, one_year.month, one_year.day)
    query = session.query(measurement.date, measurement.prcp).filter(measurement.date >= prev_year)\
        .order_by(measurement.date).all()
    precip_dict = {date: prcp for date, prcp in query}
    return jsonify(precip_dict)

@app.route("/api/v1.0/stations")
def stations():
    results = session.query(station.station).all()
    stations = list(np.ravel(results))
    return jsonify(stations= stations)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    query = session.query(measurement.date, measurement.tobs).filter(measurement.station == 'USC00519281')\
    .filter(measurement.date >= '2016-08-23').all()

    tobs = []
    for date, tob in query:
        tobs_dict = {}
        tobs_dict["Date"] = date
        tobs_dict["Tobs"] = tob
        tobs.append(tobs_dict)

    return jsonify(tobs)

@app.route("/api/v1.0/<start>")
def temps_start(start):
    session = Session(engine)
    query = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
            filter(measurement.date >= start).all()
    session.close()

    temps = []
    for min_temp, avg_temp, max_temp in query:
        temps_dict = {}
        temps_dict['Minimum Temperature'] = min_temp
        temps_dict['Average Temperature'] = avg_temp
        temps_dict['Maximum Temperature'] = max_temp
        temps.append(temps_dict)

    return jsonify(temps)

@app.route("/api/v1.0/<start>/<end>")
def temps_start_end(start, end):
    session = Session(engine)
    query = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
              filter(measurement.date >= start).filter(measurement.date <= end).all()
    session.close()

    temps = []
    for min_temp, avg_temp, max_temp in query:
        temps_dict = {}
        temps_dict['Minimum Temperature'] = min_temp
        temps_dict['Average Temperature'] = avg_temp
        temps_dict['Maximum Temperature'] = max_temp
        temps.append(temps_dict)

    return jsonify(temps)

if __name__ == '__main__':
    app.run(debug=True)