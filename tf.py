#TODO: finish realtime data
#TODO: grab data past midnight
#TODO: schedule realtime updates every minute
#TODO: schedule gtfs updates every once in a while
#TODO: move to a cheaper text service

import sys
import transitfeed
import gtfs_realtime_pb2
from urllib2 import urlopen
import time, os
from datetime import date

def getNextBusTimes(schedule, stopNumber, resultMax):
    #match stop number to actual stop in database
    stop = getStop(schedule, stopNumber)
    if stop is None:
        return None

    #get bus times for stop
    results = getStopTimes(schedule, stop)
    if results is None:
        return None

    if len(results) == 0:
        return "Unfortunately, there are no buses coming to that stop in the next 24 hours."

    #shrink the response array to request size
    if(len(results) >= resultMax): 
        results = results[0:resultMax]

    #return string of results seperated by line breaks
    return '\n'.join(results) 

def getStop(schedule, stopNumber):
    #iterate through stops in database and find stop that corresponds to stop number
    for stop in schedule.GetStopList():
        if(str(stop['stop_code']) == str(stopNumber)):
            return stop
    return None

def getStopTimes(schedule, stop):
    #set timezone and get localtime in seconds
    setTimeZoneForAgency(schedule)
    localTimeStruct = time.localtime()
    localTimeInSeconds = localTimeStruct.tm_hour*3600 + localTimeStruct.tm_min*60 + localTimeStruct.tm_sec

    fm = createRealtimeInstance()
    results = []
    for stopTimeTuple in stop.GetStopTimeTrips():
        timeInSecs = stopTimeTuple[0]
        activeDates = stopTimeTuple[1][0].service_period.ActiveDates()
        dateToday = time.strftime('%Y%m%d', localTimeStruct)
        if any(dateToday in d for d in activeDates):
            if(localTimeInSeconds < timeInSecs):
                route_id = stopTimeTuple[1][0]['route_id']
                shortName = schedule.routes[str(route_id)]['route_short_name']
                longName = schedule.routes[str(route_id)]['route_long_name']
                resultString = time.strftime('%I:%M%p', time.gmtime(timeInSecs)) + " - " + shortName + " " + longName
                results.append(resultString)
    return results

def setTimeZoneForAgency(schedule):
    #get agency timezone and set the TZ environment variable
    timeZone = schedule._agencies['YRT']['agency_timezone']
    os.environ['TZ'] = timeZone
    time.tzset()

def createScheduleInstance():
    loader = transitfeed.Loader("./google_transit.zip")
    schedule = loader.Load()
    return schedule

def createRealtimeInstance():
    fm = gtfs_realtime_pb2.FeedMessage()
    fm.ParseFromString(urlopen('http://rtu.york.ca/gtfsrealtime/TripUpdates').read())
    return fm

if __name__ == '__main__':
    schedule = createScheduleInstance()
    print getNextBusTimes(schedule, 3280, 5)
