# tle2czml


Python package which takes in Two Line Element's (TLE's) and returns a czml file visualising their orbits.  
  
<a href="https://pypi.python.org/pypi/tle2czml">https://pypi.python.org/pypi/tle2czml</a>


## Background  
CZML is a JSON format for describing a time-dynamic graphical scene, primarily for display in a web browser running <a href="https://cesiumjs.org/">Cesium</a>.  
A <a href="https://www.celestrak.com/NORAD/documentation/tle-fmt.asp">TLE</a> is a data format encoding a list of orbital elements of an Earth-orbiting object for a given point in time.  

This package uses <a href="https://pypi.python.org/pypi/sgp4/">sgp4.py</a> to predict the satellites fututure postion, and a slightly modified <a href="https://github.com/cleder/czml">czml.py</a> to create the .czml files.  

![alt text](screenshot.png)

## Requirements
* python3
* pip
* Text file containing list of two line elements, example: 

```
ISS (ZARYA)             
1 25544U 98067A   20031.24963938  .00001307  00000-0  31791-4 0  9996
2 25544  51.6454 310.9655 0005435 211.0342 248.3831 15.49121879210634
NSIGHT                  
1 42726U 98067MF  20030.23762086  .00066982  00000-0  26471-3 0  9994
2 42726  51.6289 225.2148 0002096 295.3393  64.7394 15.86153189153413
KESTREL EYE IIM (KE2M)  
1 42982U 98067NE  20030.08703972  .00009357  00000-0  92741-4 0  9997
2 42982  51.6350 271.0640 0002884 271.0425  89.0241 15.66608286129206
ASTERIA                 
1 43020U 98067NH  20030.29800372  .00049876  00000-0  20399-3 0  9995
2 43020  51.6389 237.2881 0001998 250.9363 109.1425 15.85563292125443
DELLINGR (RBLE)         
1 43021U 98067NJ  20030.38822124  .00010528  00000-0  10150-3 0  9991
2 43021  51.6359 268.6360 0001491 215.4152 144.6746 15.67139053125030
```

## Install
`pip install tle2czml`

## Usage
```python
import tle2czml

# Creates a file in the current directory called "orbit.czml", containing the orbits of the satelites over the next 24 hours.
tle2czml.create_czml("tle.txt")
```

```python
import tle2czml
from datetime import datetime

# You can specify the time range you would like to visualise
start_time = datetime(2019, 2, 1, 17, 30)
end_time = datetime(2019, 2, 2, 19, 30)
tle2czml.create_czml("tle.txt", start_time=start_time, end_time=end_time)
```

```python
import tle2czml

# You can also specify a different output path
tle2czml.create_czml("tle.txt", outputfile_path="other_orbit_file.czml")
```

## View Orbits
To view the orbits, go to `https://cesiumjs.org/Cesium/Build/Apps/CesiumViewer/`, and drag the .czml file into the browser.
(Click the "Play" button in the bottom left corner to start the visualisation)  

You can find up to date TLE's for most satellites on `https://www.celestrak.com/NORAD/elements/`  

## To Do
* Add command line script
* Allow users to login with space-track.org
* Add ability to select base64 image to use for satellite
* Add ability to generate html file with cesium globle displaying czml file
