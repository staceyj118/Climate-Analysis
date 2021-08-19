from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
import datetime as dt
import numpy as np

app=Flask(__name__)

@app.route('/')

def home():
    return (f"Welcome to the home page!<br/>"
          f"Here are your available routes:<br/>"
          f"/api/v1.0/precipitation<br/>"
          f"/api/v1.0/stations<br/>"
          f"/api/v1.0/tobs<br/>"
          f"/api/v1.0/start/end<br/>")

engine = create_engine("sqlite:///hawaii.sqlite")


Base=automap_base()
Base.prepare(engine, reflect=True)
Measurement=Base.classes.measurement
Station=Base.classes.station
session = Session(engine)
prev_date=dt.date(2017,8,23)-dt.timedelta(days=365)

# Perform a query to retrieve the data and precipitation scores
results=session.query(Measurement.prcp, Measurement.date).filter(Measurement.date>prev_date).all()


@app.route('/api/v1.0/precipitation')
def precipitation():

    precipitation=[]

    for prcp, date in results:
        precipitationDict={}
        precipitationDict['prcp']=prcp
        precipitationDict['date']=date
        precipitation.append(precipitationDict)
        session.clear
    return jsonify(precipitation)

@app.route('/api/v1.0/stations')
def stations():

    stations=session.query(Measurement.station).distinct().all()
    all_stations = list(np.ravel(stations))

    return jsonify({"stations":all_stations})

@app.route('/api/v1.0/tobs')
def tobs():

    results=session.query(Measurement.tobs).filter(Measurement.station=='USC00516128').filter(Measurement.date>prev_date).all()
    tobs_result=list(np.ravel(results))
    session.clear
    return jsonify({"tobs":tobs_result})

@app.route('/api/v1.0/<start_date>')
def start(start_date=None):
    sel=[func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)]
    results=session.query(*sel).filter(Measurement.date>=start_date).all()
    temperatures=[]
    for TMIN, TMAX, TAVG in results:
        TDictionary={}
        TDictionary['TMIN']=TMIN
        TDictionary['TMAX']=TMAX
        TDictionary['TAVG']=TAVG
        temperatures.append(TDictionary)
        session.clear
    return jsonify(temperatures)

@app.route('/api/v1.0/<start_date>/<end_date>')
def start_end(start_date=None,end_date=None):
    sel=[func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)]
    results=session.query(*sel).filter(Measurement.date>=start_date).filter(Measurement.date<=end_date).all()
    temps=list(np.ravel(results))
    session.clear
    return jsonify(temps=temps)



app.run(debug=True)
session.close()
