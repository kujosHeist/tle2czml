# this module contains classes and scripts for generating the .czml files used to visualize the satellites orbits

from .czml import CZML
from .czml import CZMLPacket
from .czml import Description
from .czml import Billboard
from .czml import Label
from .czml import Path
from .czml import Position

from datetime import datetime, timedelta
from dateutil import parser
import math, sys, getopt, pkg_resources, pytz

from sgp4.io import twoline2rv
from sgp4.earth_gravity import wgs72


BILLBOARD_SCALE = 1.5
SATELITE_IMAGE_URI = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAADJSURBVDhPnZHRDcMgEEMZjVEYpaNklIzSEfLfD4qNnXAJSFWfhO7w2Zc0Tf9QG2rXrEzSUeZLOGm47WoH95x3Hl3jEgilvDgsOQUTqsNl68ezEwn1vae6lceSEEYvvWNT/Rxc4CXQNGadho1NXoJ+9iaqc2xi2xbt23PJCDIB6TQjOC6Bho/sDy3fBQT8PrVhibU7yBFcEPaRxOoeTwbwByCOYf9VGp1BYI1BA+EeHhmfzKbBoJEQwn1yzUZtyspIQUha85MpkNIXB7GizqDEECsAAAAASUVORK5CYII="
LABEL_FONT = "11pt Lucida Console"

MULTIPLIER = 60
DESCRIPTION_TEMPLATE = 'Orbit of Satellite: '
MINUTES_IN_DAY = 1440
TIME_STEP = 300

DEFAUlead_times_RGBA = [213, 255, 0, 255]
DEBUGGING = False

class Satellite:
	'Common base class for all satellites'

	def __init__(self, raw_tle, tle_object, rgba):
		self.raw_tle = raw_tle
		self.tle_object = tle_object  # sgp4Object
		self.rgba = rgba
		self.sat_name = raw_tle[0].rstrip()	
		# extracts the number of orbits per day from the tle and calcualtes the time per orbit
		self.orbital_time_in_minutes = (24.0/float(self.raw_tle[2][52:63]))*60.0 
		self.tle_epoch = tle_object.epoch
		
	def get_satellite_name(self):
		return self.satName
		
class Colors:
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
		next_color = self.rgbs[self.index]
		if self.index < len(self.rgbs) - 1:
			self.index += 1
		else:
			self.index = 0
			
		return next_color
		
		
# create CZML doc with default document packet
def create_czml_file(start_time, end_time):
	interval = get_interval(start_time, end_time)
	doc = CZML()
	packet = CZMLPacket(id='document', version='1.0')
	print(interval)
	print(start_time.isoformat())			

	packet.clock = {"interval": interval, "currentTime": start_time.isoformat(), "multiplier": MULTIPLIER, "range": "LOOP_STOP", "step": "SYSTEM_CLOCK_MULTIPLIER"}
	doc.packets.append(packet)
	return doc
	

def create_satellite_packet(sat_id, tle, orbit_time_in_minutes, sim_start_time, sim_end_time, rgba):
	availability = get_interval(sim_start_time, sim_end_time)
	packet = CZMLPacket(id='Satellite/{}'.format(sat_id))
	packet.availability = availability
	packet.description = Description("{} {}".format(DESCRIPTION_TEMPLATE, sat_id))
	packet.billboard = create_bill_board()
	packet.label = create_label(sat_id, rgba)
	packet.path = create_path(availability, orbit_time_in_minutes, rgba, sim_start_time, sim_end_time)
	packet.position = create_position(sim_start_time, sim_end_time, tle)  
	return packet	


def create_bill_board():
	bb = Billboard(scale=BILLBOARD_SCALE, show=True)
	bb.image = SATELITE_IMAGE_URI
	return bb

def create_label(sat_id, rgba):
	lab = Label(text=sat_id, show=True)
	lab.fillColor = {"rgba": rgba}
	lab.font = LABEL_FONT
	lab.horizontalOrigin = "LEFT"
	lab.outlineColor = {"rgba": [0,0,0,255]}
	lab.outlineWidth = 2	 
	lab.pixelOffset = {"cartesian2": [12,0]} 
	lab.style = 'FILL_AND_OUTLINE'
	lab.verticalOrigin = 'CENTER'
	return lab
	
	
def create_path(total_path_interval, orbit_time_in_minutes, rgba, sim_start_time, sim_end_time):
	p = Path()
	
	p.show = [{"interval": total_path_interval, "boolean": True}]
	p.width = 1
	p.material = {"solidColor": {"color": {"rgba": rgba}}}
	p.resolution = 120

	start_epoch_str = total_path_interval.split("/")[0]
	end_epoch_str = total_path_interval.split("/")[1]

	MINUTES_IN_SIM = int((sim_end_time - sim_start_time).total_seconds()/60)
	
	left_over_minutes = MINUTES_IN_SIM % orbit_time_in_minutes 
	number_of_full_orbits = math.floor(MINUTES_IN_SIM/orbit_time_in_minutes)
	
	sub_path_interval_start = parser.parse(start_epoch_str)
	# first interval roughly half an orbit, rest of the path intervals are full orbits
	sub_path_interval_end = sub_path_interval_start + timedelta(minutes=left_over_minutes)    
	sub_path_interval_str = sub_path_interval_start.isoformat() + '/' + sub_path_interval_end.isoformat()

	orbital_time_in_seconds = (orbit_time_in_minutes * 60.0)
	
	if DEBUGGING:
		print('Total Path Interval: ' + total_path_interval)   # goes from tle epoch to 12/24 hours in future
	
	lead_times = []
	
	end_epoch = parser.parse(end_epoch_str)
	
	for i in range(0, number_of_full_orbits + 1):
		lead_times.append({
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
		sub_path_interval_end = sub_path_interval_start + timedelta(minutes=orbit_time_in_minutes)
		sub_path_interval_str = sub_path_interval_start.isoformat() + '/' + sub_path_interval_end.isoformat()
	
	if DEBUGGING:
		print()
	
	sub_path_interval_start = parser.parse(start_epoch_str)
	# first interval roughly half an orbit, rest of the path intervals are full orbits
	sub_path_interval_end = sub_path_interval_start + timedelta(minutes = left_over_minutes)  
	sub_path_interval_str = sub_path_interval_start.isoformat() + '/' + sub_path_interval_end.isoformat()	
	
	trail_times = []
	
	for i in range(0, number_of_full_orbits + 1):
		trail_times.append({
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
		sub_path_interval_end = sub_path_interval_start + timedelta(minutes=orbit_time_in_minutes)
		
		sub_path_interval_str = sub_path_interval_start.isoformat() + '/' + sub_path_interval_end.isoformat()	

	p.leadTime = lead_times
	p.trailTime = trail_times	
	
	return p


def create_position(start_time, end_time, tle):
	pos = Position()
	pos.interpolationAlgorithm = "LAGRANGE"
	pos.interpolationDegree = 5
	pos.referenceFrame = "INERTIAL"
	pos.epoch = start_time.isoformat()
	
	diff = end_time - start_time
	number_of_positions = int(diff.total_seconds()/300)   
	# so that there's more than one position
	number_of_positions += 5;  
	pos.cartesian = get_future_sat_positions(tle, number_of_positions, start_time)
	return pos	


def get_interval(current_time, end_time):
	return current_time.isoformat() + "/" + end_time.isoformat()
	
def get_future_sat_positions(satTle, number_of_positions, start_time):
	time_step = 0
	output = []
	epoch = start_time
	for i in range(0, number_of_positions):
		current_time = start_time + timedelta(seconds=time_step)
		eci_position, eci_velocity = satTle.propagate(current_time.year, current_time.month, current_time.day, current_time.hour, current_time.minute, current_time.second)
	
		output.append(time_step)
		output.append(eci_position[0] * 1000)  # converts km's to m's
		output.append(eci_position[1] * 1000)
		output.append(eci_position[2] * 1000)
		time_step += TIME_STEP
	
	return output
	
def get_satellite_orbit(raw_tle, sim_start_time, sim_end_time, czml_file_name):
	sat_name = raw_tle[0]
	tle_sgp4 = twoline2rv(raw_tle[1], raw_tle[2], wgs72)

	sat = Satellite(raw_tle, tle_sgp4, DEFAUlead_times_RGBA)
	doc = create_czml_file(sim_start_time, sim_end_time)
	
	if DEBUGGING:
		print()
		print('Satellite Name: ', sat.satName)
		print('TLE Epoch: ', sat.tleEpoch)
		print('Orbit time in Minutes: ', sat.orbitalTimeInMinutes)	
		print()
	
	sat_packet = create_satellite_packet(sat.sat_name, sat.tle_object, sat.orbital_time_in_minutes, sim_start_time, sim_end_time, sat.rgba)
	doc.packets.append(sat_packet)
	doc.write(czml_file_name)		


def read_tles(tle_file_name, rgbs):
	tle_src = open(tle_file_name, 'r')
	raw_tle = []
	sats = []

	i = 1
	for line in tle_src:
		raw_tle.append(line)
		
		if i % 3 == 0:
			tle_object = twoline2rv(raw_tle[1], raw_tle[2], wgs72)
			sats.append(Satellite(raw_tle, tle_object, rgbs.get_next_color()))
			raw_tle = []
		i+=1
	
	return sats		


def create_czml(inputfile_path, outputfile_path=None, start_time=None, end_time=None):
	"""
	Takes in a file of TLE's and returns a CZML file visualising their orbits.
	"""	

	rgbs = Colors()
	satellite_array = read_tles(inputfile_path, rgbs)
	
	if not start_time:
		start_time = datetime.utcnow().replace(tzinfo=pytz.UTC)

	if not end_time:
		end_time = start_time + timedelta(hours=24)

	doc = create_czml_file(start_time, end_time)

	for sat in satellite_array:
		sat_name = sat.sat_name
		orbit_time_in_minutes = sat.orbital_time_in_minutes
		tle_epoch = sat.tle_epoch

		print()
		print('Satellite Name: ', sat_name)
		print('TLE Epoch: ', tle_epoch)
		print('Orbit time in Minutes: ', orbit_time_in_minutes)	
		print()
		
		sat_packet = create_satellite_packet(sat.sat_name, sat.tle_object, sat.orbital_time_in_minutes, start_time, end_time, sat.rgba)

		doc.packets.append(sat_packet)

	if not outputfile_path:
		outputfile_path = "orbit.czml"
	doc.write(outputfile_path)
