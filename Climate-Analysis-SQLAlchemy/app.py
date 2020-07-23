import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

################################################
#Database Setup
################################################
engine = create_engine('sqlite:///hawaii.sqlite')

#reflect an existing database into a new model
Base = automap_base()
#reflect the tables
Base.prepare(engine,reflect=True)

#Save references to each table
Measurement = Base.classes.Measurement
Station = Base.classes.Station

#Create our session (link) from Python to the DB
session = Session(engine)

################################################
#Flask Setup
################################################
app = Flask(_name_)

################################################
#Flask Routes
################################################
@app.route('/')
def welcome():
    return (
        f"Welcomw to the Hawaii Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start/end<br/>"
    )

@app.rout("/api/v1.0/precipitation")
def precipitation():
    """Return the precipitation data for the last year"""
    #Calculate the date 1 year ago from last date in database
    prev_year = dt.date(2018,8,23) - dt.timedelta(days=365)

    #Query for the date and precipitation for the last year
    precipitation = session.query(Measurement.date, Measurement.prcp).\
                            filter(Measurement.date >= prev_year).all()
    precip = {}
    for date,prcp in precipitation:
        precip[date] = prcp
    return jsonify(precip)

@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations."""
    results = session.query(Station.station).all()

    #Unravel results into a 1D array and convert to a list
    stations = list(np.ravel(results))
    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def temp_monthly():
    """Return the temperature observations (tobs) for previous year."""
    #Calculate the date 1 year ago from last date in database
    prev_year = dt.date(2018,8,23) - dt.timedelta(days=365)

    #Query the primary station for all tobs from the last yer
    results = session.query(Measurement.tobs).\
                    filter(Measurement.date >= prev_year).all().\
                    filter(Measure.station == 'USC00519281')

    #Unravel results into a 1D array and convert to a list
    temps = list(np.ravel(results))

    #Return the results
    return jsonify(temps)

@app.route('api/v1.0/<start>')
@app.route('/api/v1.0/<start>/<end>')
def stats(start,end):
    """Return TMIN, TAVH, TMAX"""

    #Select statement
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end:
        # calculate TMIN, TAVG, TMAX for dates greater than start
        results = session.query(*sel).\
                filter(Measurement.date >= start).all()
        # Unravel results into a 1D array and convert to a list
        temps = list(np.ravel(results))
        return jsonify(temps)
    
    # calculate TMIN, TAVG, TMAX with start and stop
    results = session.query(*sel).\
                    filter(Measurement.date >= start).\
                    filter(Measurement.date <= end).all()
    # Unravel results into a 1D array and convert to a list
    temps = list(np.ravel(results))
    return jsonify(temps)

if __name__ == '__main__':
    app.run()