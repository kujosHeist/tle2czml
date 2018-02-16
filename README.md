# tle2czml


Python package which takes a file of Two Line Element's (TLE's) and returns a czml file visualising their orbits.  

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
1 25544U 98067A   18046.55817189  .00001353  00000-0  27714-4 0  9990
2 25544  51.6417 265.0608 0003589 103.0964 344.3049 15.54096060 99608
TIANGONG 1              
1 37820U 11053A   18046.58112813  .00094150  12300-4  13743-3 0  9998
2 37820  42.7514 126.9107 0017316  32.3682  67.8761 16.04338150366699
AGGIESAT 4              
1 41313U 98067HP  18046.57341670  .00209614  31071-4  29378-3 0  9994
2 41313  51.6292 173.0661 0005230 335.8780  24.1986 16.05344224117524
FLOCK 2E'-1             
1 41479U 98067HZ  18046.59084296  .00067088  00000-0  22534-3 0  9995
2 41479  51.6287 200.4285 0001834 261.2577  98.8221 15.89445123100275
FLOCK 2E'-3             
1 41480U 98067JA  18046.62549195  .00058065  00000-0  22549-3 0  9996
2 41480  51.6222 201.3651 0000797 288.7159  71.3758 15.86570970100255
```

## Install
`pip install tle2czml`

## Usage
```python
import tle2czml

# This creates a file in the current directory called "orbit.czml", containing the orbits of the satelites over the next 24 hours.
tle2czml.create_czml("tle.txt")

# You can also specify the time range you would like to visualise the orbits
start_time = datetime(2018, 2, 1, 17, 30)
end_time = datetime(2018, 2, 1, 19, 30)
tle2czml.create_czml(input_file, start_time=start_time, end_time=end_time)

# You can specify a different output path
tle2czml.create_czml(input_file, outputfile_path="path/to/orbit.czml")
```

## View Orbits
To view the orbits, go to `https://cesiumjs.org/Cesium/Build/Apps/CesiumViewer/`, and drag the .czml file into the browser.
(Click the "Play" button in the bottom left corner to start the visualisation)  

You can find up to date TLE's for most satellites on `https://www.celestrak.com/NORAD/elements/`  

## To Do
* Add command line script
* Allow users to login with space-track.org
* Add tests
* Add ability to select base64 image to use for satellite
* Add ability to generate html file with cesium globle showing czml file