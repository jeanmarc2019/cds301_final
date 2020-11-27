import numpy as np
from latlongHelper import batchAddressConverter
from fairfaxCountyHelper import generateSourceData

def scrapeData(arguments):

    entries = generateSourceData(
        arguments["targetCityStateZip"].split(' ')[-1],
        limit=arguments["sampleSize"],
        aprType=arguments["appraisalType"],
        additionalZips=arguments["additionalZips"],
        dbData=arguments["dbData"]
    )

    numberOfEntries = len(entries['address'])

    # gets coordinates and calculates distances between them
    entries['lat'] = []
    entries['long'] = []
    locationsLatLong = batchAddressConverter(
        entries['address'],
        entries['citystatezip'],
        arguments["mapQuestKey"]
    )
    for location in locationsLatLong:
        entries['lat'].append(location[0])
        entries['long'].append(location[1])

    # lets you know something went terribly wrong :(
    for key in entries.keys():
        if numberOfEntries != len(entries[key]):
            print("WARNING: number of addresses (%d) does not equal number of %s (%d)",
                  (numberOfEntries, key, len(entries[key]))
                  )
            return False

    entries['name'] = [entries['address'][i] + ', ' + entries['citystatezip'][i] for i in range(len(entries['address']))]

    return entries

# Polynomial Regression
def polyfit(x, y, degree):
    results = {}

    coeffs = np.polyfit(x, y, degree)

     # Polynomial Coefficients
    results['polynomial'] = coeffs.tolist()

    # r-squared
    p = np.poly1d(coeffs)
    # fit values, and mean
    yhat = p(x)                         # or [p(z) for z in x]
    ybar = np.sum(y)/len(y)          # or sum(y)/len(y)
    ssreg = np.sum((yhat-ybar)**2)   # or sum([ (yihat - ybar)**2 for yihat in yhat])
    sstot = np.sum((y - ybar)**2)    # or sum([ (yi - ybar)**2 for yi in y])
    results['determination'] = ssreg / sstot

    return results