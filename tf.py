#TODO: finish realtime data
#TODO: schedule realtime updates every minute
#TODO: schedule gtfs updates every once in a while
#TODO: move to a cheaper text service

import sys
import transitfeed
import gtfs_realtime_pb2
from urllib2 import urlopen
import time, os
from datetime import date

realtime = None
realtimeAge = None

def getNextBusTimes(schedule, stopNumber, resultMax):
    #match stop number to actual stop in database
    stop = getStop(schedule, stopNumber)
    if stop is None:
        return None

    #get bus times for stop
    results = getStopTimes(schedule, stop)
    if results is None:
        return "Unfortunately, there are no buses coming to that stop in the next 24 hours."

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

    #compute localtime in seconds and create date strings for today and tomorrow
    localTimeStruct = time.localtime()
    localTimeInSeconds = getTimeInSecondsFromTimeStruct(localTimeStruct)
    dateToday = time.strftime('%Y%m%d', localTimeStruct)

    tomorrowTimeStruct = time.localtime(time.time() + 24*3600)
    dateTomorrow = time.strftime('%Y%m%d', tomorrowTimeStruct)

    results = {}
    resultsTomorrow = {}

    createRealtimeInstance()

    for trip in stop.GetStopTimeTrips():
        arrivalTimeInSecs = trip[0]
        activeDates = trip[1][0].service_period.ActiveDates()

        if any(dateToday in d for d in activeDates):
            if(localTimeInSeconds < arrivalTimeInSecs):
                route = trip[1][0]
                arrivalTimeInSecs = updateArrivalWithRealtime(realtime, route, arrivalTimeInSecs)
                resultString = createStopTimeString(schedule, route, arrivalTimeInSecs)
                results[resultString] = arrivalTimeInSecs

        if any(dateTomorrow in d for d in activeDates):
            route = trip[1][0]
            resultString = createStopTimeString(schedule, route, arrivalTimeInSecs)
            resultsTomorrow[resultString] = arrivalTimeInSecs

    combinedSortedResults = sorted(results, key=results.get) + sorted(resultsTomorrow, key=resultsTomorrow.get)
    return combinedSortedResults

def updateArrivalWithRealtime(realtime, route, arrivalTimeInSecs):
    # if(any(route.trip_id in entity.trip_update.trip.trip_id for entity in realtime.entity)):        
    #     entity = next(entity for entity in realtime.entity if entity.trip_update.trip.trip_id == route.trip_id)
    #     if entity:
    #         stopTimeUpdate = next(stop for stop in entity.trip_update.stop_time_update if stop.stop_sequence != index)
    #         if stopTimeUpdate:
    #             for stopTimeUpdate in entity.trip_update.stop_time_update:
    #                 arrivalTimeInSecs = time.localtime(stopTimeUpdate.departure.time)
    return arrivalTimeInSecs

def createStopTimeString(schedule, route, arrivalTimeInSecs):
    route_id = route['route_id']
    shortName = schedule.routes[str(route_id)]['route_short_name']
    longName = schedule.routes[str(route_id)]['route_long_name']
    resultString = time.strftime('%I:%M%p', time.gmtime(arrivalTimeInSecs)) + " - " + shortName + " " + longName
    return resultString


def getTimeInSecondsFromTimeStruct(timeStruct):
    return timeStruct.tm_hour*3600 + timeStruct.tm_min*60 + timeStruct.tm_sec

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
    global realtime
    global realtimeAge
    if realtimeAge and ((time.time() - realtimeAge) < 120):
        print "No update"
        return
    print "update"
    realtimeAge = time.time()
    realtime = gtfs_realtime_pb2.FeedMessage()
    realtime.ParseFromString(urlopen('http://rtu.york.ca/gtfsrealtime/TripUpdates').read())

if __name__ == '__main__':
    schedule = createScheduleInstance()
    print getNextBusTimes(schedule, 3280, 3)
