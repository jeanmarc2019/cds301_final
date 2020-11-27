import requests, random
import pandas as pd

locationLookUpUrl = "https://services1.arcgis.com/ioennV6PpG5Xodq0/ArcGIS/rest/services/OpenData_A2/FeatureServer/0/"
assessedValUrl = "https://services1.arcgis.com/ioennV6PpG5Xodq0/ArcGIS/rest/services/OpenData_A6/FeatureServer/2/"
def getObjectsByZip(zip, limit):
    address = locationLookUpUrl + "query?where=ZIP%3D"+str(zip)+"&objectIds=&time=&geometry=&geometryType=esriGeometryEnvelope&inSR=&spatialRel=esriSpatialRelIntersects&resultType=none&distance=0.0&units=esriSRUnit_Meter&returnGeodetic=false&outFields=&returnGeometry=true&featureEncoding=esriDefault&multipatchOption=xyFootprint&maxAllowableOffset=&geometryPrecision=&outSR=&datumTransformation=&applyVCSProjection=false&returnIdsOnly=true&returnUniqueIdsOnly=false&returnCountOnly=false&returnExtentOnly=false&returnQueryGeometry=false&returnDistinctValues=false&cacheHint=false&orderByFields=&groupByFieldsForStatistics=&outStatistics=&having=&resultOffset=&resultRecordCount=&returnZ=false&returnM=false&returnExceededLimitFeatures=true&quantizationParameters=&sqlFormat=none&f=pjson&token="
    headers = {'Accept': 'application/json'}
    r = requests.get(url = address, headers=headers)
    objectIDs = r.json()["objectIds"]
    output = {}

    # limits higher than 10 take a while
    checkLimitValue = limit if len(objectIDs) > limit else len(objectIDs) - 1
    indeces = random.sample(range(len(objectIDs)), checkLimitValue) if limit != None else range(len(objectIDs))
    for index in indeces:
        progress(len(output), len(indeces))
        address = locationLookUpUrl + str(objectIDs[index]) + "?f=pjson"
        r2 = requests.get(url=address, headers=headers)
        objectAttr = r2.json()["feature"]["attributes"]
        output[str(objectAttr["PARCEL_PIN"])] = {
            'address': str(objectAttr["ADDRESS_1"]),
            'citystatezip': objectAttr["CITY"] + ' ' + objectAttr["STATE"] + ' ' + objectAttr["ZIP"]
        }
    print("\nDONE\n")
    return output
def getAssessedValue(parid, aprType):
    address = assessedValUrl + "query?where=PARID%3D'"+parid.replace(" ", "+")+"'&objectIds=&time=&resultType=none&outFields=&returnIdsOnly=true&returnUniqueIdsOnly=false&returnCountOnly=false&returnDistinctValues=false&cacheHint=false&orderByFields=&groupByFieldsForStatistics=&outStatistics=&having=&resultOffset=&resultRecordCount=&sqlFormat=none&f=pjson&token="
    headers = {'Accept': 'application/json'}
    r = requests.get(url=address, headers=headers)

    # it SHOULDN'T ever be greater than 1, but it's a precaution
    if len(r.json()["objectIds"]) >= 1:
        address = assessedValUrl + str(r.json()["objectIds"][0]) + "?f=pjson"
        r2 = requests.get(url = address, headers=headers)
        return r2.json()["feature"]["attributes"][aprType]
    else:
        return None

def getAddress(parid):
    address = locationLookUpUrl + '/query?where=PARCEL_PIN%3D\'' + str(parid) + '\'&objectIds=&time=&resultType=none&outFields=&returnIdsOnly=true&returnUniqueIdsOnly=false&returnCountOnly=false&returnDistinctValues=false&cacheHint=false&orderByFields=&groupByFieldsForStatistics=&outStatistics=&having=&resultOffset=&resultRecordCount=&sqlFormat=none&f=pjson&token='
    headers = {'Accept': 'application/json'}
    r = requests.get(url=address, headers=headers)
    # print(r.json())
    if len(r.json()["objectIds"]) == 0:
        return None
    address = locationLookUpUrl + str(r.json()["objectIds"][0]) + "?f=pjson"
    r2 = requests.get(url=address, headers=headers)
    objectAttr = r2.json()["feature"]["attributes"]
    return (str(objectAttr["ADDRESS_1"]), objectAttr["CITY"] + ' ' + objectAttr["STATE"] + ' ' + objectAttr["ZIP"])

def generateSourceData(zip, limit, aprType, additionalZips, dbData):
    print("Generating base data...")
    status = ""
    output = {
        'address': [],
        'citystatezip': [],
        'price': []
    }
    if dbData == "":
        baseData = getObjectsByZip(zip, limit)
        for additionalZip in additionalZips:
            print("Generating data for additional zipcode " + additionalZip + "...")
            baseData = {**baseData, **getObjectsByZip(additionalZip,limit)}

        print('Processing data... This might take a while...')
        for parid in baseData.keys():
            progress(len(output['price']), limit * (len(additionalZips) + 1), status)
            status = ""
            assessedVal = getAssessedValue(parid, aprType)
            if assessedVal == None or parid == None:
                status = str(parid) + " had no assessments attached to it"
                continue # skips bad entries
            output['price'].append(getAssessedValue(parid, aprType))
            output['address'].append(baseData[parid]['address'])
            output['citystatezip'].append(baseData[parid]['citystatezip'])
    else:
        print('Processing data from csv... This might take a while...')
        baseData = pd.read_csv(dbData)
        count_row = baseData.shape[0]
        # forces limit from config if it contains for rows than the limit
        if count_row > limit:
            count_row = limit
        for index, row in baseData.iterrows():
            if index == count_row:
                break
            progress(index, count_row, status)
            status = ""
            locationData = getAddress(row['PARID'])
            if locationData == None:
                continue
            output['price'].append(row['PRICE'])
            output['address'].append(locationData[0])
            output['citystatezip'].append(locationData[1])
    print("\nDONE\n" + str(output))
    return output

def progress(count, total, status=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    print('[%s] %s%s ...%s\r' % (bar, percents, '%', status), end="")