# -*- coding:utf-8 _*-
"""
@author:lpf
@file: tle2czml.py
@time: 2023/5/10  14:18
"""

from tle2czml.tle2czml import Tle2Czml


def tset():
    tles = '''BEIDOU 2
    1 31115U 07011A   21323.16884980 -.00000043  00000-0  00000-0 0  9993
    2 31115  51.9034 274.7604 0003928 314.2233  45.7206  1.77349177 46511
    BEIDOU 3
    1 36287U 10001A   21323.54986160 -.00000268  00000-0  00000-0 0  9995
    2 36287   1.7347  43.1625 0001966  74.6398 279.3247  1.00266671 43404'''
    t2c = Tle2Czml()
    czml = t2c.tles_to_czml(tles)
    print(type(czml))
    print(type(czml.dumps()))
    print(czml.dumps())


if __name__ == '__main__':
    tset()
