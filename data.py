import sqlite3
import time
from datetime import datetime

conn = sqlite3.connect('yrtGTFS.db')
c = conn.cursor()

def getNextBuses(stopNumber):
    stopID = ""
    for row in c.execute('SELECT * FROM gtfs_stops WHERE stop_code LIKE ' + stopNumber):
        stopID = str(row[0]) 
    if stopID == "":
        print "throw error"

#TODO: consider time zone for server location
#TODO: consider data from the correct date/handle calendar dates
    currentTime = datetime.time(datetime.now())
    currentTimeInSeconds = currentTime.hour*3600 + currentTime.minute*60 + currentTime.second

    results = []

    for stopTime in c.execute('SELECT * FROM gtfs_stop_times WHERE stop_id = ' + stopID + ' ORDER BY arrival_time'):
       timeStruct = time.strptime(stopTime[1],"%H:%M:%S")
       timeInSeconds = timeStruct.tm_hour * 3600 + timeStruct.tm_min * 60 + timeStruct.tm_sec
       if(timeInSeconds > currentTimeInSeconds):
           for trip in c.execute('SELECT * FROM gtfs_trips WHERE trip_id =' + stopTime[0]):
              for route in c.execute('SELECT * FROM gtfs_routes WHERE route_id= ' + trip[0]):
                  results.append(stopTime[1] + " - " + route[2] + " " + route[3])
    resultString = ""
    for result in results:
        resultString += " " + result + " \n"
    return resultString

if __name__ == '__main__':
    print getNextBuses("3280")
