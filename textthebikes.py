import requests, json

def get_all_docks():
	station_json=requests.get("http://www.citibikenyc.com/stations/json").content
	#this gives us a list of dictionaries. each dictionary is a station+ info
	station_list=json.loads(station_json)["stationBeanList"]
	station_dict={}
	for station in station_list:
		station_id = station["id"]
		del station["id"]
		station_dict[station_id]=station

	return station_dict



def find_close_stations(lat, lng):
	"""Pass in user's lat and long. Return station id for closest 5 stations."""






