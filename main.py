'''
Jamie/Kiya
OC Transit API Interaction

'''


import datetime
import time
import json
import requests

# Every minute make a call to designated stop
# Grab the expected stop time and the ETA,
# Push the ETA to a list and update the stop time.  (Dict?)
# when the stop time disappears from the request, calculate the difference between the arrival time and the schedule

#Due to the way ETA and such is handled by the API, to calculate how late a bus is we need to add find it's departing
# time from it's genesis station and subtract the GPS ETA. 

def getOCData():#Core Function
    url = ''
    #Definitions of key variables
    _appID = '' #Changed for Privacy
    _apiKey = '' #Changed for Privacy
    _routeNo = '' #Changed for Privacy
    _stopNo = '' #Changed for Privacy
    _format = 'json' 
    r = requests.get(url='https://api.octranspo1.com/v1.3/GetNextTripsForStop',
                     params=dict(appID=_appID, apiKey=_apiKey, routeNo=_routeNo, stopNo=_stopNo, format=_format)) #
    return (json.loads(r.text)) #Returns the retrieved JSON

    # if(datetime.now().weekday() < 6):
ex = open("time.txt","a+") #creates output text file, later imported into google sheets and analysed.
ex.writelines("GPS AT | SCH AT | ETA | Diff\n") #Header for the
ex.close() #Memory conservation
while True: #always on, ineffecient but suits smaller project.
    _delay = 7;
    try: #The JSON will sometimes return empty when there is too large of a gap between trips (ie midnight to 5am)
        data = getOCData() #grabs JSON
        d = data["GetNextTripsForStopResult"]["Route"]["RouteDirection"]["Trips"]["Trip"] #Looks this section of JSON
        for i in d: #Runs through provided trips (max 3)
            ex = open("time.txt","a+") #Reopen text file
            timeNow = datetime.datetime.now() - datetime.timedelta(hours=5) #Calculate Naive time now (time is
            # returned UTC)
            schedArr = datetime.datetime.strptime(i['TripStartTime'], "%H:%M").replace(year=timeNow.year,
                                                                                       month=timeNow.month,
                                                                                       day=timeNow.day) + \
                       datetime.timedelta(
                           minutes=_delay) #Specific stop is delay minutes after first
            timeETA = int(i['AdjustedScheduleTime']) #GPS ETA
            timeArrive = timeNow + datetime.timedelta(minutes=timeETA) #The current time plus the GPS ETA is the 
            # scheduled arrival 
            tdelta = schedArr - timeNow #time difference between the scheduled Arrival and when it arrived.
            taDelta =  timeArrive - schedArr #+ datetime.timedelta(days=1)
            print(timeArrive.strftime("%H:%M"), schedArr.strftime("%H:%M"), i['AdjustedScheduleTime'],
                  round((taDelta.seconds / 60),2)) #Print calculated info
            if (timeETA < 2 and timeETA != -1): #When the bus arrives (GPS is <2 minutes)
                #Update the file with Scheduled Arrival, Actual and the difference.
                ex.writelines(str(timeArrive.strftime("%H:%M ") + schedArr.strftime("| %H:%M | ") + i[
                    'AdjustedScheduleTime'] + " | " +
                                  str(round((taDelta.seconds / 60), 2))) + " | " + str(timeNow.strftime("%d/%m/%y") + '\n'))
                print("----------------")
                #Flags an arrival
                print("DING", "SchedArrive:", schedArr.strftime("%H:%M"), "ActArrive", timeNow.strftime("%H:%M"),
                      "Difference:", round((tdelta.seconds / 60), 2))
                time.sleep(60)
                print("----------------")
        print("----------------")
        ex.close()
        time.sleep(60)
    except: 
        time.sleep(120)
