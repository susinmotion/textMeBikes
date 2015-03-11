import copy
import googlemaps
import math
import os
import requests, json

class NoStationsError(Exception): pass

LAT_DEGREES_DIFF = .003 # approx. 0.2 miles in degrees latitude (in NYC)
LNG_DEGREES_DIFF = .004 # approx. 0.2 mile in degrees longitude (in NYC)
MIN_NUM_STATIONS = 5 # min. number of stations that must be return

gmaps = googlemaps.Client(key=os.environ['GOOGLE_MAPS_API_KEY'])

def get_all_docks():
    """Get a huge dict. of all CitiBike docks from the CitiBike website."""
    station_json = requests.get("http://www.citibikenyc.com/stations/json").content
    # this gives us a list of dictionaries. each dictionary is a
        # station id --> dict. of station info
    station_list = json.loads(station_json)["stationBeanList"]
    station_dict = {}
    for station in station_list:
        station_id = station["id"]
        del station["id"]
        station_dict[station_id]=station

    return station_dict

def find_near_stations(lat, lng, station_dict, iters=1):
    """Pass in user's lat and long. Return station id for closest 5+ stations.

    Look for stations in a .2-mile radius (then clean results of any inactive stations).
    If left with more than min. # of required results, return. Else, repeat the
    process with a widened radius (i.e. by incrementing `iters`)."""
    # TODO: hardcode bounds of legal lat/lng = 1.5ish miles in all directions
        # from Astor Place (so no requests from Harlem, Kansas, etc.)
    if iters > 8:
        raise NoStationsError("I guess there are no stations near you. Womp.")
    near_stations = {}
    for station_id, station_info in station_dict.iteritems():
        if (lat - iters * LAT_DEGREES_DIFF) <= station_info["latitude"] <= (lat + iters * LAT_DEGREES_DIFF) and \
            (lng - iters * LNG_DEGREES_DIFF) <= station_info["longitude"] <= (lng + iters * LNG_DEGREES_DIFF):
            near_stations[station_id] = station_info

    near_stations = clean_stations(near_stations)
    if len(near_stations) < MIN_NUM_STATIONS:
        near_stations = find_near_stations(lat, lng, station_dict, iters=iters+1)
    return near_stations

def clean_stations(near_stations,bikes_only=False, docks_only=False):
    """Take the results of find_near_stations and remove any that are not in service."""
    cleaned_station_dict = copy.deepcopy(near_stations)
    for station_id, station_info in near_stations.iteritems():
        if station_info["statusValue"] != "In Service":
            del cleaned_station_dict[station_id]

    return cleaned_station_dict
    # TODO: IF LOOKING FOR JUST BIKES/DOCKS: remove if no bikes/docks

def sort_stations(lat, lng, near_stations_dict):
    """Given a dict. of stations, returns a list of station IDs sorted
        according to dist. from given coord's."""
    for station_info in near_stations_dict.values():
        station_info["dist_from_target"] = distance(lat, lng,
                                            station_info["latitude"],
                                            station_info["longitude"])

    return sorted([station_id for station_id in near_stations_dict],
        key=lambda id: near_stations_dict[id]["dist_from_target"])

    # NOTE: so um, I'm not sure this function works. I'm getting some suspicious
        # results and I don't have time to write a proper test. Womp =(

def distance(start_lat, start_lng, end_lat, end_lng):
    """Helper function to compute the as-the-crow-files distance between two
        given points."""
        # TODO: maybe this is better done as actual walking distance, via
            # Google Maps API?
    return math.sqrt((end_lat - start_lat)**2 + (end_lng - start_lng)**2)

def in_manhattan_or_brooklyn(addr_obj):
    """A func. to filter results of a Google Maps geocode query; returns True if
        address is in Manhattan or Brooklyn, False otherwise."""
    for component in addr_obj["address_components"]:
        if "sublocality_level_1" in component["types"] and component["long_name"] in ["Manhattan", "Brooklyn"]:
            return True
    return False

def get_a_bike(station_dict):
    """The main function. Currently runs on raw input. Will eventually respond
        to txt messages."""
    print "Hi! Text a bike: please enter an address or intersection to search near:"
    addr = raw_input("> ")
    all_results = gmaps.geocode(addr)
    filtered_results = filter(in_manhattan_or_brooklyn, all_results)
    for res in filtered_results:
        # for debugging -- just to make sure we correctly processed the user's address
        print res["formatted_address"]
    if len(filtered_results) < 1:
        print "Whoops, didn't recognize that address/intersection. Please try again!"
    elif len(filtered_results) > 1:
        print """The address you entered was ambiguous, please try again. (Tips:
            make sure you clarify 'Manhattan' or 'Brooklyn'; make sure you state
            whether streets are E or W, N or S.)"""
    else: # a valid address; let's find bikes!
        the_address = filtered_results[0]
        lat = the_address["geometry"]["location"]["lat"]
        lng = the_address["geometry"]["location"]["lng"]
        near_stations = find_near_stations(lat, lng, station_dict)
        sorted_station_ids = sort_stations(lat, lng, near_stations)
        for station_id in sorted_station_ids:
            print "--> #%d: %s (%d/%d bikes)" % (
                station_id,
                near_stations[station_id]["stationName"],
                near_stations[station_id]["availableBikes"],
                near_stations[station_id]["totalDocks"]
            )

if __name__ == '__main__':
    station_dict = get_all_docks()
    get_a_bike(station_dict)
    # does this flow make sense? probs not. Change later. Just for testing purposes.



