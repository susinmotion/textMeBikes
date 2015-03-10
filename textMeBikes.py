import copy
import googlemaps
import os
import requests, json

class NoStationsError(Exception): pass

LAT_DEGREES_DIFF = .003
LNG_DEGREES_DIFF = .004
NUM_STATIONS = 5

gmaps = googlemaps.Client(key=os.environ['GOOGLE_MAPS_API_KEY'])

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
    # HARDCODE 1.5ish miles in all directions from Astor Place
    if iterations > 8:
        raise NoStationsError("I guess there are no stations near you. Womp.")
    near_stations = {}
    for station_id, station_info in station_dict.iteritems():
        if (lat - iterations * LAT_DEGREES_DIFF) <= station_info["latitude"] <= (lat + iterations * LAT_DEGREES_DIFF) and \
            (lng - iterations * LNG_DEGREES_DIFF) <= station_info["longitude"] <= (lng + iterations * LNG_DEGREES_DIFF):
            near_stations[station_id] = station_info

    near_stations = clean_stations(near_stations)
    if len(near_stations) < NUM_STATIONS:
        near_stations = find_near_stations(lat, lng, station_dict, iterations=iterations+1)
    return near_stations

def clean_stations(near_stations,bikes_only=False, docks_only=False):
    cleaned_station_dict = copy.deepcopy(near_stations)
    for station_id, station_info in near_stations.iteritems():
        if station_info["statusValue"] != "In Service":
            del cleaned_station_dict[station_id]

    return cleaned_station_dict

    # TODO: IF LOOKING FOR JUST BIKES/DOCKS: remove if no bikes/docks

def in_manhattan_or_brooklyn(addr_obj):
    for component in addr_obj["address_components"]:
        if "sublocality_level_1" in component["types"] and component["long_name"] in ["Manhattan", "Brooklyn"]:
            return True
    return False

def get_a_bike(station_dict):
    print "Hi! Text a bike: please enter an address or intersection to search near:"
    addr = raw_input("> ")
    all_results = gmaps.geocode(addr)
    filtered_results = filter(in_manhattan_or_brooklyn, all_results)
    for res in filtered_results:
        print res["formatted_address"]
    if len(filtered_results) < 1:
        print "Whoops, didn't recognize that address/intersection. Please try again!"
    elif len(filtered_results) > 1:
        print "The address you entered was ambiguous, please try again. (Tips: make sure you clarify 'Manhattan' or 'Brooklyn'; make sure you state whether streets are E or W, N or S.)"
    else: # a valid address; let's find bikes!
        the_address = filtered_results[0]
        lat = the_address["geometry"]["location"]["lat"]
        lng = the_address["geometry"]["location"]["lng"]
        near_stations = find_near_stations(lat, lng, station_dict)
        for station_id in near_stations:
            print "--> %s: %d/%d bikes" % (
                near_stations[station_id]["stationName"],
                near_stations[station_id]["availableBikes"],
                near_stations[station_id]["totalDocks"]
            )

if __name__ == '__main__':
    station_dict = get_all_docks()
    get_a_bike(station_dict)
    # does this flow make sense? probs not. Change later. Just for testing purposes.



