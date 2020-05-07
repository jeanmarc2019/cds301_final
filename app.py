import plotly.express as px
import pandas as pd
from latlongHelper import addressToLatLong, batchAddressConverter, calculateDistance, batchDistanceCalculation
from fairfaxCountyHelper import generateSourceData

# initial variables
mapQuestKey = "" # REQUIRED: get key from mapquest https://developer.mapquest.com/
targetAddress = "" # (optional) <street number> <name> <type> e.g. 1234 anywhere blvd
targetCityStateZip = "" # (optional) <city> <state abbreviation> <zip> e.g. Podunk VA 20170
appraisalType = "APRTOT" # appraisal options are APRTOT, APRBLDG, and APRLAND
sampleSize = 3 # anything higher than 10 takes a while TODO: optimize code to decrease time
numOfBins = 8
colors = []

def create_bins(lower_bound, width, quantity):
    bins = []
    for low in range(lower_bound,
                     lower_bound + quantity * width + 1, width):
        bins.append((low, low + width))
    return bins


def find_bin(value, bins):
    for i in range(0, len(bins)):
        if bins[i][0] <= value < bins[i][1]:
            return i
    return -1

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
lats = []
longs = []
for location in locationsLatLong:
    lats.append(location[0])
    longs.append(location[1])

# meanPrice = 0
# sigma = 0
# for price in entries['price']:
#     meanPrice += price
# meanPrice /= len(entries['price'])
# for price in entries['price']:
#     sigma += (price - meanPrice) ** 2
# sigma /= len(entries['price'])
# sigma **= 0.5
# bins = create_bins(lower_bound=min(entries['price']),
#                    width=sigma,
#                    quantity=numOfBins)
# entries['bin'] = [find_bin(entries['price'][i], bins) for i in range(len(entries['price']))]

combinedNames = [entries['address'][i] + ', ' + entries['citystatezip'][i] for i in range(len(entries['address']))]

name = targetAddress if targetAddress != "1908 Reston Station Blvd" else "Wiehle-Reston East Metro"
df = pd.DataFrame(dict(distance=entries['distance'], price=entries['price'],
                       name=combinedNames, lats=lats, longs=longs))
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
# add target address
lats.append(convertedTarget[0])
longs.append(convertedTarget[1])
combinedNames.append(targetAddress)
entries['distance'].append(0)
entries['price'].append(0)
df = pd.DataFrame(dict(distance=entries['distance'], price=entries['price'],
                       name=combinedNames, lats=lats, longs=longs))
fig = px.scatter_mapbox(df, lat="lats", lon="longs", hover_name="name", hover_data=['price'],
                        color_discrete_sequence=["fuchsia"], zoom=15, height=600,
                        center=dict(lat=convertedTarget[0], lon=convertedTarget[1]))
fig.update_layout(mapbox_style="open-street-map")
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
fig.show()