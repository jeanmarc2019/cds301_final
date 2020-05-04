import plotly.express as px
import pandas as pd
from latlongHelper import addressToLatLong, batchAddressConverter, calculateDistance, batchDistanceCalculation
from fairfaxCountyHelper import generateSourceData

# initial variables
mapQuestKey = "" # REQUIRED: get key from mapquest https://developer.mapquest.com/
targetAddress = "" # (optional) <street number> <name> <type> e.g. 1234 anywhere blvd
targetCityStateZip = "" # (optional) <city> <state abbreviation> <zip> e.g. Podunk VA 20170
appraisalType = "APRTOT" # appraisal options are APRTOT, APRBLDG, and APRLAND
sampleSize = 500 # anything higher than 10 takes a while TODO: optimize code to decrease time

# wiehle reston metro is default location
if targetAddress == "" or targetCityStateZip == "":
    targetAddress = "1908 Reston Station Blvd"
    targetCityStateZip = "Reston VA 20190"
convertedTarget = addressToLatLong(targetAddress, targetCityStateZip, mapQuestKey)

entries = generateSourceData(targetCityStateZip.split(' ')[-1], limit=sampleSize, aprType=appraisalType)

n_entries = len(entries['address'])
locationsLatLong = batchAddressConverter(entries['address'], entries['citystatezip'], mapQuestKey)
entries['distance'] = batchDistanceCalculation(locationsLatLong, convertedTarget)

print("Generating plotly graph...")
# If something fails here, it's because the lengths don't match
print(len(entries['address']))
print(len(entries['citystatezip']))
print(len(entries['distance']))
print(len(entries['price']))
combinedNames = [entries['address'][i] + ', ' + entries['citystatezip'][i] for i in range(len(entries['address']))]
df = pd.DataFrame(dict(distance=entries['distance'], price=entries['price'],
                       name=combinedNames))

name = targetAddress if targetAddress != "1908 Reston Station Blvd" else "Wiehle-Reston East Metro"
# Use column names of df for the different parameters x, y, color, ...
fig = px.scatter(df, x="distance", y="price",
                 title="Distance From "+name+" vs. Price",
                 hover_name="name", hover_data=['name'],
                )
fig.update_layout(
    xaxis=dict(
        range=(0, int(max(entries['distance'])+2)),
        constrain='domain'
    )
)
print("DONE")
fig.show()