import requests, json

class NoStationsError(Exception): pass

LAT_DEGREES_DIFF = .003
LNG_DEGREES_DIFF = .004
NUM_STATIONS = 5

def get_all_docks():
	station_json = requests.get("http://www.citibikenyc.com/stations/json").content
	#this gives us a list of dictionaries. each dictionary is a station+ info
	station_list = json.loads(station_json)["stationBeanList"]
	station_dict = {}
	for station in station_list:
		station_id = station["id"]
		del station["id"]
		station_dict[station_id]=station

	return station_dict

def find_near_stations(lat, lng, station_dict, iterations=1):
	"""Pass in user's lat and long. Return station id for closest 5 stations."""
	# TODO: check that user gives a legal lat/lng (e.g. not all the way uptown, in Kansas, etc.)

	if iterations > 100:
		raise NoStationsError("I guess there are no stations near you. Womp.")
	near_stations = {}
	for station_id, station_info in station_dict.iteritems():
		if (lat - iterations * LAT_DEGREES_DIFF) <= station_info["latitude"] <= (lat + iterations * LAT_DEGREES_DIFF) and \
			(lng - iterations * LNG_DEGREES_DIFF) <= station_info["longitude"] <= (lng + iterations * LNG_DEGREES_DIFF):
			near_stations[station_id] = station_info

	clean_stations(near_stations)
	if len(near_stations) < NUM_STATIONS:
		near_stations = find_near_stations(lat, lng, station_dict, iterations=iterations+1)
	print iterations
	return near_stations

def clean_stations(near_stations,bikes_only=False, docks_only=False):
	for station_id, station_info in near_stations.iteritems():
		if station_info["statusValue"] != "In Service":
			del near_stations[station_id]

	# if status not 'good', remove
	# IF LOOKING FOR JUST BIKES/DOCKS: remove if no bikes/docks
	# if not enough stations,





