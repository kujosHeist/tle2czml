#  Shane Carty - 12713771
#  Orbital Prediction for Earth Observation

#  Overpass test script

import ephem

from ephem import degrees
import dateutil.tz
import dateutil.parser

from dateutil import parser

from datetime import datetime
from datetime import timedelta

from coordinate_conversion import *


def datetime_from_time(tr):
    year, month, day, hour, minute, second = tr.tuple()
    dt = datetime(year, month, day, hour, minute, int(second))
    return dt


def get_next_pass(lon, lat, alt, observer_time, tle):

    sat = ephem.readtle(str(tle[0]), str(tle[1]), str(tle[2]))

    observer = ephem.Observer()
    observer.lat = str(lat)
    observer.long = str(lon)
    observer.elevation = alt
    observer.pressure = 0
    observer.horizon = '-0:34' # to account for refraction of light at the horizon

    observer.date = observer_time

    # observer date is automatically given current date and time

    tr, azr, mt, altt, ts, azs = observer.next_pass(sat)


    duration = int((ts - tr) *60*60*24)
    rise_time = datetime_from_time(tr)
    max_time = datetime_from_time(mt)
    set_time = datetime_from_time(ts)

    observer.date = max_time

    sun = ephem.Sun()
    sun.compute(observer)

    sat.compute(observer)

    sun_alt = ephem.degrees(sun.alt)
    print("alt: " + str(sun.alt))
    print("eclipsed: " + str(sat.eclipsed))



    visible = False
    if sat.eclipsed is False and -18 < sun_alt < -6:
        visible = True

    return {
        "rise_time": rise_time,
        "max_time": str(max_time),
        "set_time": str(set_time),

        "rise_azimuth": degrees(azr),
        "max_alt": degrees(altt),
        "set_azimuth": degrees(azs),
        "sun_alt":sun_alt,
        "visible": visible

           }


def get_next_passes(lon, lat, alt, start_time, end_time, tle):

    sat = ephem.readtle(str(tle[0]), str(tle[1]), str(tle[2]))


    observer = ephem.Observer()
    observer.lat = str(lat)
    observer.long = str(lon)
    observer.elevation = alt
    observer.pressure = 0
    observer.horizon = '-0:34'

    dictList = []
    while start_time < end_time:


        observer.date = start_time

        tr, azr, mt, altt, ts, azs = observer.next_pass(sat)

        duration = int((ts - tr) *60*60*24)
        rise_time = datetime_from_time(tr)
        max_time = datetime_from_time(mt)
        set_time = datetime_from_time(ts)

        observer.date = max_time

        sun = ephem.Sun()
        sun.compute(observer)
        sat.compute(observer)

        sun_alt = degrees(sun.alt)


        visible = False
        if sat.eclipsed is False and -18 < sun_alt < -6:
            visible = True

        if(set_time < end_time):
            dictList.append({
                "rise_time": rise_time,
                "set_time": str(set_time),

                "rise_azimuth": degrees(azr),
                "set_azimuth": degrees(azs),

                "max_time": str(max_time),
                "max_alt": degrees(altt),
              
                "visible": visible
            })

        start_time = set_time + timedelta(minutes=10)



        
    return dictList           


line1 = 'ISS (ZARYA)'             
line2 = '1 25544U 98067A   15309.28862034  .00009990  00000-0  15401-3 0  9992'
line3 = '2 25544  51.6449  99.8552 0006738 109.1634 323.6990 15.54818572969997'
tle = [line1, line2, line3 ]

lat = 53.3083013
longitude = -6.2231407999999995
alt = 0
now = datetime.now()

def runTest():
    data = get_next_passes(longitude, lat, alt, now, now + timedelta(days=2), tle)

    for res in data:
        for key in res:
            print(key + " " + str(res[key]))
        print()


def runTest1():

    info = get_next_pass(longitude, lat, alt, datetime.now(), tle)

    print(getLLA(4521,4528,1452,57333.27777777777))

    print("rise time: " + str(info["rise_time"]) )
    print("max time: " + str(info["max_time"]))
    print("set time: " + str(info["set_time"]))
    print()
    print("rise azimuth: " + str(info['rise_azimuth']))
    print("max alt: " + str(info['max_alt']))
    print("set azimuth: " + str(info['set_azimuth']))


    sun_alt = info['sun_alt']
    print()
    print("sun_alt: " + str(sun_alt))

    print(str(degrees('-6')))

    b = degrees('-18') < sun_alt < degrees('-6')
    print(b)

runTest1()





       