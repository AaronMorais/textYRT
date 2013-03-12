#TODO: consider time zone for server location
#TODO: consider data from the correct day/week/holdidays/weekend/other
#TODO: add realtime data
#TODO: grab data past midnight

import sqlite3
import time, os
from datetime import datetime

conn = sqlite3.connect('yrtGTFS.db')
c = conn.cursor()
def getNextBuses(stopNumber, resultMax):
    stopID = getStopID(stopNumber)
    if stopID is None:
        return ""

    results = getStopResults(stopID)
    if results is None:
        return ""

    if(len(results) >= resultMax):
        results = results[0:resultMax]
    return '\n'.join(results)

def getStopResults(stopID):
    c.execute('SELECT * FROM gtfs_agency')
    timeZone = c.fetchone()[3]
    os.environ['TZ'] = timeZone
    time.tzset()
    currentTime = time.localtime()
    currentTimeInSeconds = currentTime.tm_hour*3600 + currentTime.tm_min*60 + currentTime.tm_sec
    results = []
    t = (stopID,)
    c.execute('SELECT * FROM gtfs_stop_times WHERE stop_id =? ORDER BY arrival_time', t)
    stopTimes = c.fetchall()
    for stopTime in stopTimes:
        timeInSecs = stopTime[10]
        if(currentTimeInSeconds < timeInSecs):
            resultString = stopTime[1] + " - " + getRouteInfo(stopTime[0])
            results.append(resultString)
    return results

def getRouteInfo(tripID):
    t = (tripID,)
    c.execute('SELECT * FROM gtfs_trips WHERE trip_id =?', t)
    t = (c.fetchone()[0],)
    c.execute('SELECT * FROM gtfs_routes WHERE route_id =?', t)
    info = c.fetchone()
    return info[2] + " " + info[3]


def getStopID(stopNumber):
    t = (stopNumber,)
    c.execute('SELECT * FROM gtfs_stops WHERE stop_code =?', t)
    return c.fetchone()[0]

if __name__ == '__main__':
  print getNextBuses("3280", 5)
