import requests, json, time, random, urllib.parse
# TODO: follow up with Zillow, as their system for generating API keys is down
# For use in data scraper, running query on each entry from public tax info (which is down right now)
# Parameters
zwsid = "" # Enter ID generated from registering on the Zillow website
address = ""
citystatezip = ""

# Actual part that does stuff
parameters = {
    'zws-id': zwsid,
    'address': urllib.parse.quote(address),
    'citystatezip': urllib.parse.quote(citystatezip),
    'rentzestimate': True
}
searchEndpoint = "http://www.zillow.com/webservice/Directory.htm"
headers = {'Accept': 'application/json'}
def get_submission_records(try_number=1):
    try:
        r = requests.get(url = searchEndpoint, headers=headers, params = parameters)
        print(r.text)
        data = r.json()
    except (requests.exceptions.ConnectionError, json.decoder.JSONDecodeError):
        time.sleep(2**try_number + random.random()*0.01) #exponential backoff
        return get_submission_records(try_number=try_number+1)
    else:
        return data
print(get_submission_records())