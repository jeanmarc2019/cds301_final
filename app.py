import plotly.express as px
import numpy as np
import pandas as pd
from latlongHelper import addressToLatLong, batchDistanceCalculation
from scraper import scrapeData, polyfit

# initial variables
# arguments = {
#     # wiehle reston metro is default location Lake Fairfax Dr, Reston, VA 20190
#     'targetAddress': "1908 Reston Station Blvd", # (optional) <street number> <name> <type> e.g. 1234 anywhere blvd
#     'targetCityStateZip': "Reston VA 20190", # (optional) <city> <state abbreviation> <zip> e.g. Podunk VA 20170
#     'mapQuestKey': "h57onIjVo4j1MAvNzvfpXw19M8sWs1QD", # REQUIRED: get key from mapquest https://developer.mapquest.com/
#     'additionalZips': ["20192", "20191", "20170", "20194"], # (optional) enter other zip codes near the area you are looking at for wider area
#     'appraisalType': "APRTOT", # appraisal options are APRTOT, APRBLDG, and APRLAND
#     'sampleSize': 100, # anything higher than 10 takes a while
#     'zScoreLimitPrice': 100, # (float > 0) refinement level of data
#     'zScoreLimitDistance': 100, # (float > 0) refinement level of distance
#     'maximumDistance': 100, # (float > 0) used to prevent weird considerations of locations of places in other states
#     'maximumPrice': 20000000, # (float > 0) used to prevent insane prices from throwing things off
#     'increments': 0.375, # (maximumDistance > float > 0) at what increments the data zooms into the center each iteration
#     'iterations': 4, # (int > 0) number of iterations to run the tool
#     'csvPath': "entries_1908 Reston Station Blvd_reducedFairfax.csv.csv", # path of scraped data you wish to use.  Otherwise runs scraper
#     # 'csvPath': "", # path of scraped data you wish to use.  Otherwise runs scraper
#     'dbData': "pulledData.csv" # used to specify a dataset of pre-existing entries that contain PARID and PRICE columns
# }
def make_visualization(arguments):
    convertedTarget = addressToLatLong(
        arguments["targetAddress"],
        arguments["targetCityStateZip"],
        arguments["mapQuestKey"]
    )
    targetName = arguments["targetAddress"] if arguments["targetAddress"] != "1908 Reston Station Blvd" else "Wiehle-Reston East Metro"
    arguments['sampleSize'] = int(arguments['sampleSize'])
    arguments['zScoreLimitPrice'] = int(arguments['zScoreLimitPrice'])
    arguments['zScoreLimitDistance'] = int(arguments['zScoreLimitDistance'])
    arguments['maximumDistance'] = float(arguments['maximumDistance'])
    arguments['maximumPrice'] = float(arguments['maximumPrice'])
    arguments['increments'] = float(arguments['increments'])
    arguments['iterations'] = int(arguments['iterations'])
    if arguments['csvPath'] == "":
        entries = scrapeData(arguments)
        # saves last scrape to csv
        rawLocationDf = pd.DataFrame(entries)
        if (arguments["dbData"] == ""):
            rawLocationDf.to_csv(
                'entries_' + arguments["targetAddress"] +
                '_samplesize' + str(arguments['sampleSize']) +
                '_' + str(len(arguments['additionalZips']) + 1) +
                'zips.csv',
                index=False
            )
        else:
            rawLocationDf.to_csv(
                'entries_' + arguments["targetAddress"] +
                '_' + arguments["dbData"] + '.csv',
                index=False
            )
    else:
        entries = pd.read_csv(arguments['csvPath']).to_dict(orient='list')

    entries['distance'] = batchDistanceCalculation(
        [(entries['lat'][i], entries['long'][i]) for i in range(len(entries['address']))],
        convertedTarget
    )
    entriesAtLevel = {key: value[:] for key, value in entries.items()}
    generated_figs = []
    for iteration in range(arguments["iterations"]):
        distanceAtLevel = arguments['maximumDistance'] - arguments["increments"] * iteration
        if distanceAtLevel < 0:
            print("OH NO, distance is below zero")
            break
        # refines data based on distance
        i = 0
        startLen = len(entriesAtLevel['distance'])
        while i < len(entriesAtLevel['distance']):
            if entriesAtLevel['distance'][i] > distanceAtLevel:
                for value in entriesAtLevel.values():
                    value.pop(i)
                continue
            if entriesAtLevel['price'][i] > arguments["maximumPrice"]:
                for value in entriesAtLevel.values():
                    value.pop(i)
                continue
            i += 1
        if len(entriesAtLevel['distance']) == 0:
            print("Distance was too small and now there's nothing to show")
            break
        print("Distance refinement removed " + str(startLen - len(entriesAtLevel['distance'])) + " entriesAtLevel")

        sigmaPrice, meanPrice = np.std(entriesAtLevel['price']), np.mean(entriesAtLevel['price'])
        sigmaDistance, meanDistance = np.std(entriesAtLevel['distance']), np.mean(entriesAtLevel['distance'])

        # refines data based on maximum z-score allowed
        i = 0
        startLen = len(entriesAtLevel['price'])
        while i < len(entriesAtLevel['price']):
            zScorePrice = np.abs((entriesAtLevel['price'][i] - meanPrice) / sigmaPrice)
            zScoreDistance = np.abs((entriesAtLevel['distance'][i] - meanDistance) / sigmaDistance)
            if zScorePrice > arguments['zScoreLimitPrice'] or zScoreDistance > arguments['zScoreLimitDistance']:
                for value in entriesAtLevel.values():
                    value.pop(i)
                continue
            i += 1
        Rsquared = polyfit(entriesAtLevel['distance'], entriesAtLevel['price'], 1)
        if len(entriesAtLevel['price']) == 0:
            print("Refinement was too high and there's nothing to display")
        else:
            print("Z-Score refinement removed " + str(startLen - len(entriesAtLevel['price'])) + " entriesAtLevel")
            df = pd.DataFrame(dict(distance=entriesAtLevel['distance'], price=entriesAtLevel['price'],
                                   name=entriesAtLevel['name'], lat=entriesAtLevel['lat'], long=entriesAtLevel['long']))
            # Use column names of df for the different parameters x, y, color, ...
            fig = px.scatter(df, x="distance", y="price",
                             title="Distance From " + targetName + " vs. Price",
                             hover_name="name", hover_data=['name'], trendline="ols"
                            )
            fig.update_layout(
                xaxis_title="Distance (miles)",
                yaxis_title="Tax Assessment (USD)"
            )
            # filename = "./visualizations/" +\
            #                 targetName + "Distance" +\
            #                 str(distanceAtLevel) +\
            #                 "Rsquared" + str(round(Rsquared['determination'], 3)) + ".png"
            # f = open(filename, "w+")
            # f.close()
            # fig.write_image(filename)
            # fig.show()
            # add target address
            entriesAtLevel['lat'].append(convertedTarget[0])
            entriesAtLevel['long'].append(convertedTarget[1])
            entriesAtLevel['name'].append(targetName)
            entriesAtLevel['distance'].append(None)
            entriesAtLevel['price'].append(None)
            df = pd.DataFrame(dict(distance=entriesAtLevel['distance'], price=entriesAtLevel['price'],
                                   name=entriesAtLevel['name'], lat=entriesAtLevel['lat'], long=entriesAtLevel['long'])
                              )
            fig = px.scatter_mapbox(df, lat="lat", lon="long", hover_name="name", hover_data=['price'],
                                    color='price', zoom=13, height=600,
                                    center=dict(lat=convertedTarget[0], lon=convertedTarget[1]))
            fig.update_layout(mapbox_style="open-street-map")
            fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
            filename = "./html_vis/map" + str(iteration) + ".html"
            # f = open(filename, "w+")
            # f.close()
            fig.write_html(filename, auto_open=False)
            generated_figs.append("./html_vis/"+ filename + ".html")
            print("DONE")
        entriesAtLevel = {key: value[:] for key, value in entries.items()}
    return generated_figs
