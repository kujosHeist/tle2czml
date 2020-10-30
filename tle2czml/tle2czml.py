''' generates .czml file or json used to visualize the satellites orbits '''

import math
from datetime import datetime, timedelta

import pkg_resources
import pytz
from dateutil import parser
from sgp4.earth_gravity import wgs72
from sgp4.io import twoline2rv

from .czml import (CZML, Billboard, CZMLPacket, Description, Label, Path,
                   Position)

BILLBOARD_SCALE = 1.5
LABEL_FONT = "11pt Lucida Console"
SATELITE_IMAGE_URI = ("data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAAXNS" +
                      "R0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAADJSURBVDhPnZ" +
                      "HRDcMgEEMZjVEYpaNklIzSEfLfD4qNnXAJSFWfhO7w2Zc0Tf9QG2rXrEzSUeZLOGm47WoH95x3" +
                      "Hl3jEgilvDgsOQUTqsNl68ezEwn1vae6lceSEEYvvWNT/Rxc4CXQNGadho1NXoJ+9iaqc2xi2x" +
                      "bt23PJCDIB6TQjOC6Bho/sDy3fBQT8PrVhibU7yBFcEPaRxOoeTwbwByCOYf9VGp1BYI1BA+Ee" +
                      "HhmfzKbBoJEQwn1yzUZtyspIQUha85MpkNIXB7GizqDEECsAAAAASUVORK5CYII=")

MULTIPLIER = 60
DESCRIPTION_TEMPLATE = 'Orbit of Satellite: '
MINUTES_IN_DAY = 1440
TIME_STEP = 300

DEFAULT_RGBA = [213, 255, 0, 255]
DEBUGGING = False


class Satellite:
    'Common base class for all satellites'

    def __init__(self, raw_tle, tle_object, rgba):
        self.raw_tle = raw_tle
        self.tle_object = tle_object  # sgp4Object
        self.rgba = rgba
        self.sat_name = raw_tle[0].rstrip()
        # extracts the number of orbits per day from the tle and calcualtes the time per orbit
        self.orbital_time_in_minutes = (
            24.0/float(self.raw_tle[2][52:63]))*60.0
        self.tle_epoch = tle_object.epoch

    def get_satellite_name(self):
        'Returns satellite name'
        return self.sat_name

    def get_tle_epoch(self):
        'Returns tle epoch'
        return self.tle_epoch



class Colors:
    'defines rgba colors for satellites'

    def __init__(self):
        path = 'rgba_list.txt'
        filepath = pkg_resources.resource_filename(__name__, path)
        colors_file = open(filepath, 'r')

        rgbs = []

        for color in colors_file:
            rgb = color.split()
            rgb.append(255)  # append value for alpha
            rgbs.append(rgb)

        self.rgbs = rgbs
        self.index = 0

    def get_next_color(self):
        'returns next color'
        next_color = self.rgbs[self.index]
        if self.index < len(self.rgbs) - 1:
            self.index += 1
        else:
            self.index = 0

        return next_color

    def get_rgbs(self):
        'returns rgbs'
        return self.rgbs


# create CZML doc with default document packet
def create_czml_file(start_time, end_time):
    'create czml file using start_time and end_time'
    interval = get_interval(start_time, end_time)
    doc = CZML()
    packet = CZMLPacket(id='document', version='1.0')
    print(interval)
    print(start_time.isoformat())

    packet.clock = {"interval": interval, "currentTime": start_time.isoformat(
    ), "multiplier": MULTIPLIER, "range": "LOOP_STOP", "step": "SYSTEM_CLOCK_MULTIPLIER"}
    doc.packets.append(packet)
    return doc


def create_satellite_packet(sat, sim_start_time, sim_end_time):
    'Takes a satelite and returns its orbit'
    availability = get_interval(sim_start_time, sim_end_time)
    packet = CZMLPacket(id='Satellite/{}'.format(sat.sat_name))
    packet.availability = availability
    packet.description = Description("{} {}".format(DESCRIPTION_TEMPLATE, sat.sat_name))
    packet.billboard = create_bill_board()
    packet.label = create_label(sat.sat_name, sat.rgba)
    packet.path = create_path(availability, sat, sim_start_time, sim_end_time)
    packet.position = create_position(sim_start_time, sim_end_time, sat.tle_object)
    return packet


def create_bill_board():
    'returns a billboard'
    bill_board = Billboard(scale=BILLBOARD_SCALE, show=True)
    bill_board.image = SATELITE_IMAGE_URI
    return bill_board


def create_label(sat_id, rgba):
    'creates a label'
    lab = Label(text=sat_id, show=True)
    lab.fillColor = {"rgba": rgba}
    lab.font = LABEL_FONT
    lab.horizontalOrigin = "LEFT"
    lab.outlineColor = {"rgba": [0, 0, 0, 255]}
    lab.outlineWidth = 2
    lab.pixelOffset = {"cartesian2": [12, 0]}
    lab.style = 'FILL_AND_OUTLINE'
    lab.verticalOrigin = 'CENTER'
    return lab


def create_path(total_path_interval, sat, sim_start_time, sim_end_time):
    'creates a lead and trailing path'
    path = Path()

    path.show = [{"interval": total_path_interval, "boolean": True}]
    path.width = 1
    path.material = {"solidColor": {"color": {"rgba": sat.rgba}}}
    path.resolution = 120

    start_epoch_str = total_path_interval.split("/")[0]

    minutes_in_sim = int((sim_end_time - sim_start_time).total_seconds()/60)

    left_over_minutes = minutes_in_sim % sat.orbital_time_in_minutes
    number_of_full_orbits = math.floor(minutes_in_sim/sat.orbital_time_in_minutes)

    sub_path_interval_start = parser.parse(start_epoch_str)
    # first interval roughly half an orbit, rest of the path intervals are full orbits
    sub_path_interval_end = sub_path_interval_start + timedelta(minutes=left_over_minutes)
    sub_path_interval_str = (sub_path_interval_start.isoformat() + '/' +
                             sub_path_interval_end.isoformat())

    orbital_time_in_seconds = (sat.orbital_time_in_minutes * 60.0)

    if DEBUGGING:
        # goes from tle epoch to 12/24 hours in future
        print('Total Path Interval: ' + total_path_interval)

    lead_or_trail_times = []

    for _ in range(number_of_full_orbits + 1):
        lead_or_trail_times.append({
            "interval": sub_path_interval_str,
            "epoch": sub_path_interval_start.isoformat(),
            "number": [
                0, orbital_time_in_seconds,
                orbital_time_in_seconds, 0
            ]
        })

        if DEBUGGING:
            print('Sub interval string: ' + sub_path_interval_str)

        sub_path_interval_start = sub_path_interval_end
        sub_path_interval_end = (sub_path_interval_start +
                                 timedelta(minutes=sat.orbital_time_in_minutes))
        sub_path_interval_str = (sub_path_interval_start.isoformat() + '/' +
                                 sub_path_interval_end.isoformat())

    path.leadTime = lead_or_trail_times

    if DEBUGGING:
        print()

    sub_path_interval_start = parser.parse(start_epoch_str)
    # first interval roughly half an orbit, rest of the path intervals are full orbits
    sub_path_interval_end = sub_path_interval_start + timedelta(minutes=left_over_minutes)
    sub_path_interval_str = (sub_path_interval_start.isoformat() + '/' +
                             sub_path_interval_end.isoformat())

    lead_or_trail_times = []

    for _ in range(number_of_full_orbits + 1):
        lead_or_trail_times.append({
            "interval": sub_path_interval_str,
            "epoch": sub_path_interval_start.isoformat(),
            "number":[
                0, 0,
                orbital_time_in_seconds, orbital_time_in_seconds
            ]
        })

        if DEBUGGING:
            print('Sub interval string: ' + sub_path_interval_str)

        sub_path_interval_start = sub_path_interval_end
        sub_path_interval_end = (sub_path_interval_start +
                                 timedelta(minutes=sat.orbital_time_in_minutes))

        sub_path_interval_str = (sub_path_interval_start.isoformat() + '/' +
                                 sub_path_interval_end.isoformat())

    path.trailTime = lead_or_trail_times

    return path

def create_position(start_time, end_time, tle):
    'creates a position'
    pos = Position()
    pos.interpolationAlgorithm = "LAGRANGE"
    pos.interpolationDegree = 5
    pos.referenceFrame = "INERTIAL"
    pos.epoch = start_time.isoformat()

    diff = end_time - start_time
    number_of_positions = int(diff.total_seconds()/300)
    # so that there's more than one position
    number_of_positions += 5
    pos.cartesian = get_future_sat_positions(
        tle, number_of_positions, start_time)
    return pos


def get_interval(current_time, end_time):
    'creates an interval string'
    return current_time.isoformat() + "/" + end_time.isoformat()


def get_future_sat_positions(sat_tle, number_of_positions, start_time):
    'returns an array of satellite positions'
    time_step = 0
    output = []
    for _ in range(number_of_positions):
        current_time = start_time + timedelta(seconds=time_step)
        eci_position, _ = sat_tle.propagate(current_time.year, current_time.month, current_time.day,
                                            current_time.hour, current_time.minute,
                                            current_time.second)

        output.append(time_step)
        output.append(eci_position[0] * 1000)  # converts km's to m's
        output.append(eci_position[1] * 1000)
        output.append(eci_position[2] * 1000)
        time_step += TIME_STEP

    return output


def get_satellite_orbit(raw_tle, sim_start_time, sim_end_time, czml_file_name):
    'returns orbit of the satellite'
    tle_sgp4 = twoline2rv(raw_tle[1], raw_tle[2], wgs72)

    sat = Satellite(raw_tle, tle_sgp4, DEFAULT_RGBA)
    doc = create_czml_file(sim_start_time, sim_end_time)

    if DEBUGGING:
        print()
        print('Satellite Name: ', sat.get_satellite_name)
        print('TLE Epoch: ', sat.tle_epoch)
        print('Orbit time in Minutes: ', sat.orbital_time_in_minutes)
        print()

    sat_packet = create_satellite_packet(sat, sim_start_time, sim_end_time)
    doc.packets.append(sat_packet)
    with open(czml_file_name, 'w') as file:
        file.write(str(doc))


def read_tles(tles: str, rgbs):
    'reads tle from string'
    raw_tle = []
    sats = []

    i = 1
    for line in tles.splitlines():
        raw_tle.append(line)

        if i % 3 == 0:
            tle_object = twoline2rv(raw_tle[1], raw_tle[2], wgs72)
            sats.append(Satellite(raw_tle, tle_object, rgbs.get_next_color()))
            raw_tle = []
        i += 1

    return sats


def tles_to_czml(tles, start_time=None, end_time=None, silent=False):
    """
    Converts the contents of a TLE file to CZML and returns the JSON as a string
    """
    rgbs = Colors()
    satellite_array = read_tles(tles, rgbs)

    if not start_time:
        start_time = datetime.utcnow().replace(tzinfo=pytz.UTC)

    if not end_time:
        end_time = start_time + timedelta(hours=24)

    doc = create_czml_file(start_time, end_time)

    for sat in satellite_array:
        sat_name = sat.sat_name
        orbit_time_in_minutes = sat.orbital_time_in_minutes
        tle_epoch = sat.tle_epoch

        if not silent:
            print()
            print('Satellite Name: ', sat_name)
            print('TLE Epoch: ', tle_epoch)
            print('Orbit time in Minutes: ', orbit_time_in_minutes)
            print()

        sat_packet = create_satellite_packet(sat, start_time, end_time)

        doc.packets.append(sat_packet)

    return str(doc)


def create_czml(inputfile_path, outputfile_path=None, start_time=None, end_time=None):
    """
    Takes in a file of TLE's and returns a CZML file visualising their orbits.
    """
    with open(inputfile_path, 'r') as tle_src:
        doc = tles_to_czml(
            tle_src.read(), start_time=start_time, end_time=end_time)
        if not outputfile_path:
            outputfile_path = "orbit.czml"
        with open(outputfile_path, 'w') as file:
            file.write(str(doc))
