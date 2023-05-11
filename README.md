# tle2czml

Python package which takes in Two Line Element's (TLE's) and returns a czml file visualising their orbits.

<a href="https://pypi.python.org/pypi/tle2czml">https://pypi.python.org/pypi/tle2czml</a>

## Background

CZML is a JSON format for describing a time-dynamic graphical scene, primarily for display in a web browser
running <a href="https://cesiumjs.org/">Cesium</a>.  
A <a href="https://www.celestrak.com/NORAD/documentation/tle-fmt.asp">TLE</a> is a data format encoding a list of
orbital elements of an Earth-orbiting object for a given point in time.

This package uses <a href="https://pypi.python.org/pypi/sgp4/">sgp4.py</a> to predict the satellites fututure postion,
and a slightly modified <a href="https://github.com/cleder/czml">czml.py</a> to create the .czml files.

![alt text](screenshot.png)

## Requirements

* python3
* pip
* Text file containing list of two line elements, example:

```
ISS (ZARYA)             
1 25544U 98067A   20293.22611972  .00000497  00000-0  17003-4 0  9991
2 25544  51.6436  94.7185 0001350  46.8729 126.5595 15.49312821251249
KESTREL EYE IIM (KE2M)  
1 42982U 98067NE  20293.11355452  .00022129  00000-0  15728-3 0  9999
2 42982  51.6336   8.5058 0001619 215.9884 144.1006 15.73808685170523
DELLINGR (RBLE)         
1 43021U 98067NJ  20292.66572402  .00020201  00000-0  13900-3 0  9998
2 43021  51.6343   8.5926 0000331  53.4398 306.6632 15.74631224166254
UBAKUSAT
1 43467U 98067NQ  20293.19063114  .00070844  00000-0  29473-3 0  9996
2 43467  51.6335   1.3662 0002867   6.9343 353.1700 15.85064344139669
CUBERRT
1 43546U 98067NU  20292.65915576  .00130902  00000-0  58528-3 0  9997
2 43546  51.6326   6.1225 0002465  18.8688 341.2406 15.83306046129681
```

## Install

`pip install tle2czml`

## Usage

```python
from tle2czml.tle2czml import Tle2Czml

# Creates a file in the current directory called "orbit.czml", containing the orbits of the satelites over the next 24 hours.
t2c = Tle2Czml()
t2c.create_czml("tle.txt")
```

```python
from tle2czml.tle2czml import Tle2Czml
from datetime import datetime

# You can specify the time range you would like to visualise
start_time = datetime(2020, 10, 1, 17, 30)
end_time = datetime(2020, 10, 2, 19, 30)
t2c = Tle2Czml()
t2c.create_czml("tle.txt", start_time=start_time, end_time=end_time)
```

```python
from tle2czml.tle2czml import Tle2Czml

# You can also specify a different output path
t2c = Tle2Czml()
t2c.create_czml("tle.txt", outputfile_path="other_orbit_file.czml")
```

## Modify czml parameters

Solve the third problem.You can select base64 image to use for satellite,The parameters include BILLBOARD_SCALE
LABEL_FONT SATELITE_IMAGE_URI MULTIPLIER DESCRIPTION_TEMPLATE MINUTES_IN_DAY TIME_STEP DEFAULT_RGBA DEBUGGING. A better
improvement solution is to rewrite tle2czml as a class.Using BILLBOARD_SCALE LABEL_FONT SATELITE_IMAGE_URI MULTIPLIER
DESCRIPTION_TEMPLATE MINUTES_IN_DAY TIME_STEP DEFAULT_RGBA DEBUGGING as parameters to the class.

```python
from tle2czml.tle2czml import Tle2Czml

# multiplier affects the velocity of the orbit in Cesium，SATELLITE_IMAGE_URI affects satellite in Cesium
tles = '''BEIDOU 2
1 31115U 07011A   21323.16884980 -.00000043  00000-0  00000-0 0  9993
2 31115  51.9034 274.7604 0003928 314.2233  45.7206  1.77349177 46511
BEIDOU 3
1 36287U 10001A   21323.54986160 -.00000268  00000-0  00000-0 0  9995
2 36287   1.7347  43.1625 0001966  74.6398 279.3247  1.00266671 43404'''
t2c = Tle2Czml(multiplier=1)
czml = t2c.tles_to_czml(tles, silent=True)
print(type(czml), czml)
print(type(czml.dumps()), czml.dumps())
```

## View Orbits

To view the orbits, go to https://cesiumjs.org/Cesium/Build/Apps/CesiumViewer/ and drag the .czml file into the browser.
(Click the "Play" button in the bottom left corner to start the visualisation)

You can find up to date TLE's for most satellites on https://www.celestrak.com/NORAD/elements/

## To Do

* Add command line script
* Allow users to login with space-track.org
* Add ability to generate html file with cesium globle displaying czml file
