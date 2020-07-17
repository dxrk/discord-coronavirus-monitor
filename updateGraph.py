import requests
import json
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

headers = {
    "origin": "https://gisanddata.maps.arcgis.com",
    "referer": "https://gisanddata.maps.arcgis.com/apps/opsdashboard/index.html"
}
r = requests.get("https://services9.arcgis.com/N9p5hsImWXAccRNI/arcgis/rest/services/PmO6oUpJizhI0jM8pu3n/FeatureServer/0/query?f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&orderByFields=Report_Date_String%20asc&outSR=102100&resultOffset=0&resultRecordCount=1000&cacheHint=true", headers=headers)
recentData = r.json()

dates = []
china = []
other = []
recovered = []
confirmed = []
for date in recentData["features"]:
    dates.append(datetime.strptime(date["attributes"]["Report_Date_String"], '%Y/%m/%d'))
    china.append(date["attributes"]["Mainland_China"])
    other.append(date["attributes"]["Other_Locations"])
    recovered.append(date["attributes"]["Total_Recovered"])
    confirmed.append(date["attributes"]["Total_Confirmed"])

plt.plot(dates, china, color='tab:blue', label="Mainland China")
plt.plot(dates, other, color='tab:orange', label="Other Locations")
plt.plot(dates, recovered, color='tab:green', label="Total Recovered")
plt.plot(dates, confirmed, color='tab:red', label="Total Confirmed")
plt.xticks(rotation=45)
plt.xlabel('Dates (Timeline)')
plt.ylabel('Number of People')
plt.legend()
plt.grid()
plt.show()