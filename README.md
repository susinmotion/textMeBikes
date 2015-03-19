A program for those of us with dumbphones who ride CitiBikes (yes, we exist!) -- the ultimate goal is a service that you can text with an address/intersection, and it will text back the n (TBA) nearest CitiBike docks, as well as the number of bikes/docks at each. Shiny additional features will include being able to specify "BIKES" or "DOCKS", and have the app filter out stations with few/no [bikes/docks] remaining. Work in progress!

### Set-Up
- clone this repo (preferably into a virtualenv)
- install dependencies (`pip install -r requirements.txt`)
- from terminal, run `source environ` to borrow Maia's Google Maps API key (please be nice!)

### High-Level Overview (currently):
- user enters an address or intersection, and we run the input through the Google Maps Geocode API
    - if we get too many matches even after filtering for locations in Manhattan/Brooklyn, we can't work with this. Error message, program closes.
    - if we don't get ANY matches in Manhattan/Brooklyn, we can't work with this. Error message, program closes.
    - if we get exactly one match in Manhattan/Brooklyn, we're good to go and can find some bikes near there.
- we snag all CitiBike info from [CitiBike's giant json file](//www.citibikenyc.com/stations/json).
- we take the latitude and longitude from the given address and find all the nearby stations.
    - find nearby stations, clean the results of any not-in-service stations and check if we have enough. If not, repeat the search for nearby stations, widening the search radius.
- we sort the resultant stations by distance from the given address (currently calculated as-the-crow-flies--more useful implementation is probably to do this via walking distance as calculated by Google Maps).
- we print out the resultant stations in order of proximity to the given address, along with information of `# bikes / # docks`.

### TO-DO:
- PHONE CAPABILITY
- More tests. Like really, any tests.
- Distance --> gmaps walking distance
- Just bikes/docks
- Trim station addresses (e.g. "avenue" --> "ave")
- Cap number of responses as 160 chars
    - `more` feature? (presumably, would cache results from that phone number's last request)