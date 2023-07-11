# Import the dependencies.
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import datetime as dt
import numpy as np
#################################################
# Database Setup
#################################################
 

# create engine to hawaii.sqlite
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)


# Save the references to each table
Measurments = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)



#################################################
# Flask Setup
#################################################

app = Flask(__name__)
avaible_routes = ["/api/v1.0/precipitation","/api/v1.0/stations",\
                  "/api/v1.0/tobs", "/api/v1.0/<start>", "/api/v1.0/<start>/<end>"]


#################################################
# Flask Routes
#################################################
# defining our home page and a list containing the avaible routes 
@app.route("/")
def home():
    return (
        f"list of the avaiable routes: {avaible_routes}"
        f"available format for date entry: yyyy-mm-dd"
        )



# defining a route for pricipitation and it's calculations

@app.route("/api/v1.0/precipitation")
def pricipitation():
    recent_date = session.query(Measurments.date).group_by('date').\
    order_by(Measurments.date.desc()).first()[0]
    date_split = recent_date.split('-')
    query_date =  dt.date(int(date_split[0]), int(date_split[1]), int(date_split[2])) - dt.timedelta(days=365)
    query_date
    new = session.query(Measurments.prcp, Measurments.date).\
        filter(Measurments.date >= query_date).order_by(Measurments.date).all()
    prcp_list = []
    for result in new:
        dict = {"date":result[1], "prcp":result[0]}
        prcp_list.append(dict)
    return jsonify(prcp_list)

# defining a route for our station queries 
@app.route("/api/v1.0/stations")
def stations():
    station_query = session.query(Station.name, Station.station).all()
    station_list = []
    for station in station_query:
        dict = {"Station name":station[0], "Station":station[1]}
        station_list.append(dict)
    return jsonify(station_list)

# defining our route for temperature
@app.route("/api/v1.0/tobs")
def temperature():
    most_active_station = "USC00519281"
    temps = session.query(Measurments.tobs, Measurments.date).filter(Measurments.station == most_active_station).all()
    temp_list = []
    for tempretaure in temps:
        dict = {"date":tempretaure[1],"tobs":tempretaure[0]}
        temp_list.append(dict)
    return jsonify(temp_list)

# defining our start date page and query calculations
@app.route("/api/v1.0/<start>")
def start(start):
    TMIN = session.query(func.min(Measurments.tobs)).filter(Measurments.date >= start).all()[0][0]
    TAVG = round(session.query(func.avg(Measurments.tobs)).filter(Measurments.date >= start).all()[0][0], 2)
    TMAX = session.query(func.max(Measurments.tobs)).filter(Measurments.date >= start).all()[0][0]
    start_list = [{"TMIN":TMIN},{"TAVG":TAVG},{"TMAX":TMAX}]
    return jsonify(start_list)

# defining the last query for a start and an end points
@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    TMIN = session.query(func.min(Measurments.tobs)).filter(Measurments.date >= start, Measurments.date <= end).all()[0][0]
    TAVG = round(session.query(func.avg(Measurments.tobs)).filter(Measurments.date >= start, Measurments.date <= end).all()[0][0], 2)
    TMAX = session.query(func.max(Measurments.tobs)).filter(Measurments.date >= start, Measurments.date <= end).all()[0][0]
    start_end_list = [{"TMIN":TMIN},{"TAVG":TAVG},{"TMAX":TMAX}]
    return jsonify(start_end_list)

if __name__ == '__main__':
    app.run(debug=True)