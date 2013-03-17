import sys
import transitfeed
#TODO: consider data from the correct day/week/holdidays/weekend/other
#TODO: add realtime data
#TODO: grab data past midnight

import time, os
from datetime import date

def getNextBuses(schedule, stopNumber, resultMax):
    stop = getStop(schedule, stopNumber)
    if stop is None:
        return ""

    results = getStopResults(schedule, stop)
    if results is None:
        return ""

    if(len(results) >= resultMax):
        results = results[0:resultMax]
    return '\n'.join(results)

def getStop(schedule, stopNumber):
    for stop in schedule.GetStopList():
        if(str(stop['stop_code']) == str(stopNumber)):
            return stop
    return None

def getStopResults(schedule, stop):
    timeZone = schedule._agencies['YRT']['agency_timezone']
    os.environ['TZ'] = timeZone
    time.tzset()
    currentTime = time.localtime()
    currentTimeInSeconds = currentTime.tm_hour*3600 + currentTime.tm_min*60 + currentTime.tm_sec
    results = []
    for stopTimeTuple in stop.GetStopTimeTrips():
        timeInSecs = stopTimeTuple[0]
        activeDates = stopTimeTuple[1][0].service_period.ActiveDates()
        dateToday = time.strftime('%Y%m%d', currentTime)
        if any(dateToday in d for d in activeDates):
            if(currentTimeInSeconds < timeInSecs):
                route_id = stopTimeTuple[1][0]['route_id']
                shortName = schedule.routes[str(route_id)]['route_short_name']
                longName = schedule.routes[str(route_id)]['route_long_name']
#               hour = int(timeInSecs/3600) 
#               min = int((timeInSecs - (hour*3600))/60)
#               sec = int((timeInSecs - (hour*3600) - (min*60)))
#               resultString = str(hour) + " " + str(min) + " " + str(sec) + " - " + routeName
                resultString = time.strftime('%I:%M%p', time.gmtime(timeInSecs)) + " - " + shortName + " " + longName
                results.append(resultString)
    return results

def createScheduleInstance():
    loader = transitfeed.Loader(feed_path="./google_transit.zip")
    schedule = loader.Load()
    return schedule

if __name__ == '__main__':
    schedule = createScheduleInstance()
    print getNextBuses(schedule, 3280, 5)
