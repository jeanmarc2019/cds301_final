import plotly.express as px
import numpy as np
import pandas as pd
from latlongHelper import addressToLatLong, batchDistanceCalculation
from scraper import scrapeData

# initial variables
arguments = {
    # wiehle reston metro is default location
    'targetAddress': "1908 Reston Station Blvd", # (optional) <street number> <name> <type> e.g. 1234 anywhere blvd
    'targetCityStateZip': "Reston VA 20190", # (optional) <city> <state abbreviation> <zip> e.g. Podunk VA 20170
    'mapQuestKey': "", # REQUIRED: get key from mapquest https://developer.mapquest.com/
    'additionalZips': ["20192", "20191", "20170", "20194"], # (optional) enter other zip codes near the area you are looking at for wider area
    'appraisalType': "APRTOT", # appraisal options are APRTOT, APRBLDG, and APRLAND
    'sampleSize': 2000, # anything higher than 10 takes a while TODO: optimize code to decrease time
    'zScoreLimit': 0.1, # (float > 0) refinement level of data.  The smaller the refinement, the more accurate the data is
    'csvPath': "" # path of scraped data you wish to use.  Otherwise runs scraper
}

convertedTarget = addressToLatLong(
    arguments["targetAddress"],
    arguments["targetCityStateZip"],
    arguments["mapQuestKey"]
)
targetName = arguments["targetAddress"] if arguments["targetAddress"] != "1908 Reston Station Blvd" else "Wiehle-Reston East Metro"

if arguments['csvPath'] == "":
    entries = scrapeData(arguments)
    # saves last scrape to csv
    rawLocationDf = pd.DataFrame(entries)
    rawLocationDf.to_csv(
        'entries_' + arguments["targetAddress"] +
        '_samplesize' + str(arguments['sampleSize']) +
        '_' + str(len(arguments['additionalZips']) + 1) +
        'zips.csv',
        index=False
    )
else:
    entries = pd.read_csv(arguments['csvPath']).to_dict(orient='list')

entries['distance'] = batchDistanceCalculation(
    [(entries['lat'][i], entries['long'][i]) for i in range(len(entries['address']))],
    convertedTarget
)

sigmaPrice, meanPrice = np.std(entries['price']), np.mean(entries['price'])
sigmaDistance, meanDistance = np.std(entries['distance']), np.mean(entries['distance'])

# refines data based on maximum z-score allowed
i = 0
removed = []
while i < len(entries['price']):
    zScorePrice = np.abs((entries['price'][i] - meanPrice) / sigmaPrice)
    zScoreDistance = np.abs((entries['distance'][i] - meanDistance) / sigmaDistance)
    if zScorePrice > arguments['zScoreLimit'] or zScoreDistance > arguments['zScoreLimit']:
        for value in entries.values():
            removed.append(value.pop(i))
        continue
    i += 1
if len(entries['price']) == 0:
    print("Refinement was too high and there's nothing to display")
else:
    print("Refinement removed " + str(len(removed)) + " entries")
    df = pd.DataFrame(dict(distance=entries['distance'], price=entries['price'],
                           name=entries['name'], lat=entries['lat'], long=entries['long']))
    # Use column names of df for the different parameters x, y, color, ...
    fig = px.scatter(df, x="distance", y="price",
                     title="Distance From " + targetName + " vs. Price",
                     hover_name="name", hover_data=['name'],
                    )
    fig.update_layout(
        xaxis=dict(
            range=(0, int(max(entries['distance'])+2)),
            constrain='domain'
        )
    )
    fig.show()
    # add target address
    entries['lat'].append(convertedTarget[0])
    entries['long'].append(convertedTarget[1])
    entries['name'].append(targetName)
    entries['distance'].append(None)
    entries['price'].append(None)
    df = pd.DataFrame(dict(distance=entries['distance'], price=entries['price'],
                           name=entries['name'], lat=entries['lat'], long=entries['long'])
                      )
    fig = px.scatter_mapbox(df, lat="lat", lon="long", hover_name="name", hover_data=['price'],
                            color='price', zoom=15, height=600,
                            center=dict(lat=convertedTarget[0], lon=convertedTarget[1]))
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig.show()
    print("DONE")
