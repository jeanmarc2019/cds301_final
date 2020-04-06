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

def batchAdressConverter(addresses, citystatezips, key):
    output = []
    locationsList = []
    for i in range(len(addresses)):
        locationsList.append(addresses[i] + citystatezips[i])
    parameters = {
        'location': locationsList,
        'key': key,
    }
    searchEndpoint = "http://www.mapquestapi.com/geocoding/v1/batch"
    headers = {'Accept': 'application/json'}
    r = requests.get(url=searchEndpoint, headers=headers, params=parameters)
    for i in range(len(r.json()["results"])):
        data = r.json()["results"][i]["locations"][0]["displayLatLng"]
        output.append((data["lat"], data["lng"]))
    return output

def calculateDistance(loc1, loc2):
    # initial variables and calculations
    R = 6373.0 # radius of Earth
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
    for location in locations:
        output.append(calculateDistance(location, target))
    return output