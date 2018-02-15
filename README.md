# tle2czml

Python package which takes a file of Two Line Element's (TLE's) and returns a czml file visualising their orbits.

## Requirements
* Python3
* Pip
* File containing list of two line elements, example: 

```
ISS (ZARYA)             
1 25544U 98067A   18045.93299769  .00001486  00000-0  29736-4 0  9992
2 25544  51.6420 268.1770 0003640 101.5285  85.8672 15.54094273 99505
TIANGONG 1              
1 37820U 11053A   18046.14148403  .00095478  12401-4  13999-3 0  9993
2 37820  42.7514 129.7071 0017381  29.1995  48.6729 16.04256914366624
```


## Install
`pip install tle2czml`

## Usage
```python
import tle2czml

tleczml.create_czml("tle.txt", "out.czml")
```


## View Orbits
To view the orbits, go to `https://cesiumjs.org/Cesium/Build/Apps/CesiumViewer/`, and drag the .czml file into the browser.

You can find up to date TLE's for most satellites on `https://www.celestrak.com/NORAD/elements/`
