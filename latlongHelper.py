import requests, math

def addressToLatLong(address, citystatezip, key):
    parameters = {
        'location': address + ' ' + citystatezip,
        'key': key,
    }
    searchEndpoint = "http://open.mapquestapi.com/geocoding/v1/address"
    headers = {'Accept': 'application/json'}
    r = requests.get(url = searchEndpoint, headers=headers, params = parameters)
    data = r.json()["results"][0]["locations"][0]["displayLatLng"]
    return (data["lat"],data["lng"])

def batchAddressConverter(addresses, citystatezips, key):
    print("Converting addresses to latitudes and longitudes...")
    output = []
    locationsList = []
    for i in range(len(addresses)):
        locationsList.append(addresses[i] + citystatezips[i])
    searchEndpoint = "http://www.mapquestapi.com/geocoding/v1/batch"
    headers = {'Accept': 'application/json'}
    for i in range(int(len(locationsList)/99)+1):
        parameters = {
            'location': locationsList[99*i:99*(i+1)],
            'key': key,
        }
        r = requests.get(url=searchEndpoint, headers=headers, params=parameters)
        for j in range(len(r.json()["results"])):
            if len(r.json()["results"][j]["locations"]) == 0:
                output.append(None) # No point in trying to keep working with a bad location
                continue
            data = r.json()["results"][j]["locations"][0]["displayLatLng"]
            output.append((data["lat"], data["lng"]))
    print("DONE")
    return output

def calculateDistance(loc1, loc2):
    if loc1 == None or loc2 == None:
        return None
    # initial variables and calculations
    R = 3958.8 # radius of Earth
    lat1 = math.radians(loc1[0])
    lon1 = math.radians(loc1[1])
    lat2 = math.radians(loc2[0])
    lon2 = math.radians(loc2[1])
    dlon = lon2 - lon1
    dlat = lat2 - lat1

    # Haversine formula
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance

def batchDistanceCalculation(locations, target):
    output = []
    print("Calculating distances...")
    for location in locations:
        output.append(calculateDistance(location, target))
    print("DONE")
    return output