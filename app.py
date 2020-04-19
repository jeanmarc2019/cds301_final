import plotly.express as px
import pandas as pd
from latlongHelper import addressToLatLong, batchAdressConverter, calculateDistance, batchDistanceCalculation
from fairfaxCountyHelper import generateSourceData

# TODO: utilize public tax info to generate this, use zillowHelper.py to estimate/display realestate/rent costs
mapQuestKey = "" # REQUIRED: get key from mapquest https://developer.mapquest.com/
targetAddress = "" # (optional) <street number> <name> <type> e.g. 1234 anywhere blvd
targetCityStateZip = "" # (optional) <city> <state abbreviation> <zip> e.g. Podunk VA 20170

# wiehle reston metro is default location
if targetAddress == "" or targetCityStateZip == "":
    targetAddress = "1908 Reston Station Blvd"
    targetCityStateZip = "Reston VA 20190"
convertedTarget = addressToLatLong(targetAddress, targetCityStateZip, mapQuestKey)

entries = generateSourceData(targetCityStateZip.split(' ')[-1], limit=5, aprType='APRTOT')

n_entries = len(entries['address'])
locationsLatLong = batchAdressConverter(entries['address'], entries['citystatezip'], mapQuestKey)
entries['distance'] = batchDistanceCalculation(locationsLatLong, convertedTarget)

df = pd.DataFrame(dict(distance=entries['distance'], price=entries['price'],
                       citystatezip=entries['citystatezip']))
# Use column names of df for the different parameters x, y, color, ...
fig = px.scatter(df, x="distance", y="price",
                 title="Distance From Metro vs. Price",
                 hover_name="citystatezip", hover_data=['citystatezip'],
                )
fig.update_layout(
    xaxis=dict(
        range=(0, 10),
        constrain='domain'
    )
)

fig.show()