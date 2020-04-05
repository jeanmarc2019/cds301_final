import plotly.express as px
import pandas as pd
import csv
# TODO: utilize public tax info to generate this, use zillowHelper.py to estimate/display realestate/rent costs
entries = {
    'address': [],
    'citystatezip': [],
    'price': [],
    'distance': [],
}
with open('addresses.csv', mode='r') as infile:
    reader = csv.reader(infile)
    for row in reader:
        entries['address'].append(row[0])
        entries['citystatezip'].append(row[1])
        entries['price'].append(row[2])
        entries['distance'].append(row[3])

n_entries = len(entries['address'])

df = pd.DataFrame(dict(distance=entries['distance'], price=entries['price'],
                       citystatezip=entries['citystatezip']))
# Use column names of df for the different parameters x, y, color, ...
fig = px.scatter(df, x="distance", y="price",
                 title="Distance From Metro vs. Price",
                 hover_name="citystatezip", hover_data=['citystatezip'],
                )

fig.show()