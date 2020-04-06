import plotly.express as px
import pandas as pd
import csv
from latlongHelper import addressToLatLong, batchAdressConverter, calculateDistance, batchDistanceCalculation

# TODO: utilize public tax info to generate this, use zillowHelper.py to estimate/display realestate/rent costs
# set these before using
mapQuestKey = "" # get key from mapquest https://developer.mapquest.com/
targetAddress = "" # <street number> <name> <type> e.g. 1234 anywhere blvd
targetCityStateZip = "" # <city> <state abbreviation> <zip> e.g. Podunk VA 20170

entries = {
    'address': [],
    'citystatezip': [],
    'price': [],
    'distance': [],
}
# wiehle reston metro is default location
if targetAddress == "" or targetCityStateZip == "":
    targetAddress = "1908 Reston Station Blvd"
    targetCityStateZip = "Reston VA 20190"
convertedTarget = addressToLatLong(targetAddress, targetCityStateZip, mapQuestKey)
with open('addresses.csv', mode='r') as infile:
    reader = csv.reader(infile)
    for row in reader:
        entries['address'].append(row[0])
        entries['citystatezip'].append(row[1])
        entries['price'].append(row[2])

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
        range=(0, 2),
        constrain='domain'
    )
)

fig.show()