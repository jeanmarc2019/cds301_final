import requests, random, urllib.parse
# 0174, 0262, 0261, 0164
locationLookUpUrl = "https://services1.arcgis.com/ioennV6PpG5Xodq0/ArcGIS/rest/services/OpenData_A2/FeatureServer/0/"
assessedValUrl = "https://services1.arcgis.com/ioennV6PpG5Xodq0/ArcGIS/rest/services/OpenData_A6/FeatureServer/2/"
def getObjectsByZip(zip, limit):
    address = locationLookUpUrl + "query?where=ZIP%3D"+str(zip)+"&objectIds=&time=&geometry=&geometryType=esriGeometryEnvelope&inSR=&spatialRel=esriSpatialRelIntersects&resultType=none&distance=0.0&units=esriSRUnit_Meter&returnGeodetic=false&outFields=&returnGeometry=true&featureEncoding=esriDefault&multipatchOption=xyFootprint&maxAllowableOffset=&geometryPrecision=&outSR=&datumTransformation=&applyVCSProjection=false&returnIdsOnly=true&returnUniqueIdsOnly=false&returnCountOnly=false&returnExtentOnly=false&returnQueryGeometry=false&returnDistinctValues=false&cacheHint=false&orderByFields=&groupByFieldsForStatistics=&outStatistics=&having=&resultOffset=&resultRecordCount=&returnZ=false&returnM=false&returnExceededLimitFeatures=true&quantizationParameters=&sqlFormat=none&f=pjson&token="
    headers = {'Accept': 'application/json'}
    r = requests.get(url = address, headers=headers)
    objectIDs = r.json()["objectIds"]
    output = {}

    # limits higher than 10 take a while
    indeces = random.sample(range(len(objectIDs)), limit) if limit != None else range(len(objectIDs))
    for index in indeces:
        address = locationLookUpUrl + str(objectIDs[index]) + "?f=pjson"
        r2 = requests.get(url=address, headers=headers)
        objectAttr = r2.json()["feature"]["attributes"]
        output[str(objectAttr["PARCEL_PIN"])] = {
            'address': str(objectAttr["ADDRESS_1"]),
            'citystatezip': objectAttr["CITY"] + ' ' + objectAttr["STATE"] + ' ' + objectAttr["ZIP"]
        }
    return output
def getAssessedValue(parid, aprType):
    address = assessedValUrl + "query?where=PARID%3D'"+parid.replace(" ", "+")+"'&objectIds=&time=&resultType=none&outFields=&returnIdsOnly=true&returnUniqueIdsOnly=false&returnCountOnly=false&returnDistinctValues=false&cacheHint=false&orderByFields=&groupByFieldsForStatistics=&outStatistics=&having=&resultOffset=&resultRecordCount=&sqlFormat=none&f=pjson&token="
    headers = {'Accept': 'application/json'}
    r = requests.get(url=address, headers=headers)

    # it SHOULDN'T ever be greater than 1, but it's a precaution
    if len(r.json()["objectIds"]) > 1:
        print('WARNING: ' + parid + ' had multiple assessments assigned to it')
    address = assessedValUrl + str(r.json()["objectIds"][0]) + "?f=pjson"
    r2 = requests.get(url = address, headers=headers)
    return r2.json()["feature"]["attributes"][aprType]

def generateSourceData(zip, limit, aprType):
    print("Generating data...")
    baseData = getObjectsByZip(zip, limit)
    output = {
        'address': [],
        'citystatezip': [],
        'price': []
    }
    for parid in baseData.keys():
        output['address'].append(baseData[parid]['address'])
        output['citystatezip'].append(baseData[parid]['citystatezip'])
        output['price'].append(getAssessedValue(parid, aprType))
    print("DONE\n" + str(output))
    return output
