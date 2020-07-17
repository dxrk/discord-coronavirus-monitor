import json
import os
import sys
import random
import string
import time
from datetime import date, datetime, timedelta

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pyimgur
import pytz
import requests
import urllib3
from dhooks import Embed, Webhook

urllib3.disable_warnings()

def covidMonitor(refreshInterval):
    """
    Monitor Starts
    """
    with open('config.json') as json_file:
        configData = json.load(json_file)
    while configData['monitor'] == True:
        with open('config.json') as json_file:
            configData = json.load(json_file)
        try:
            #Defines data
            dataUpdated = False
            worldUrl = "https://services1.arcgis.com/0MSEUqKaxRlEPj5g/arcgis/rest/services/ncov_cases/FeatureServer/2/query?f=json&where=Confirmed%20%3E%200&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&orderByFields=Confirmed%20desc&resultOffset=0&resultRecordCount=100&cacheHint=true&vispogay={}".format(randomString())
            usUrl = "https://services1.arcgis.com/0MSEUqKaxRlEPj5g/arcgis/rest/services/ncov_cases/FeatureServer/1/query?f=json&where=(Confirmed%20%3E%200)%20AND%20(Country_Region%3D%27US%27)&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&orderByFields=Confirmed%20desc%2CCountry_Region%20asc%2CProvince_State%20asc&outSR=102100&resultOffset=0&resultRecordCount=250&cacheHint=true&vispogay={}".format(randomString())
            usSpecUrl = "https://services9.arcgis.com/N9p5hsImWXAccRNI/arcgis/rest/services/Nc2JKvYFoAEOFCG5JSI6/FeatureServer/1/query?f=json&where=Country_Region%3D%27US%27&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&orderByFields=Confirmed%20desc%2CCountry_Region%20asc%2CProvince_State%20asc&outSR=102100&resultOffset=0&resultRecordCount=200&cacheHint=true&vispogay={}".format(randomString())
            r = requests.get(worldUrl)
            rawWorldData = r.json()
            r4 = requests.get(usUrl)
            rawUSData = r4.json()
            headers = {
                "origin": "https://gisanddata.maps.arcgis.com",
                "referer": "https://gisanddata.maps.arcgis.com/apps/opsdashboard/index.html"
            }
            r7 = requests.get(usSpecUrl, headers=headers)
            rawUsSpecData = r7.json()

            
            if configData['world']['enabled?'] == True: 
                with open('worldData.json') as json_file:
                    worldData = json.load(json_file)
                    countries = list(worldData)
                    #Looks for non-existing countries
                    for country in rawWorldData["features"]:
                        try:
                            if country["attributes"]["Country_Region"] in countries:
                                pass
                            else:
                                worldData[country["attributes"]["Country_Region"]] = {
                                    "deaths":country["attributes"]["Deaths"],
                                    "recovered":country["attributes"]["Recovered"],
                                    "confirmed":country["attributes"]["Confirmed"]
                                }
                                timestamp = datetime.now(pytz.timezone("America/New_York")).strftime("%I:%M:%S %p %Z")
                                embed = Embed(color=16544031, title=country["attributes"]["Country_Region"], description="New country found 📰")
                                embed.add_field(name="Total Deaths", value="`{} | {:,}%`".format(country["attributes"]["Deaths"], round(country["attributes"]["Deaths"]/country["attributes"]["Confirmed"]*100, 2)), inline=True)
                                embed.add_field(name="Total Recovered", value="`{} | {:,}%`".format(country["attributes"]["Recovered"], round(country["attributes"]["Recovered"]/country["attributes"]["Confirmed"]*100, 2)), inline=True)
                                embed.add_field(name="Confirmed", value="`{}`".format(country["attributes"]["Confirmed"]), inline=True)
                                embed.set_footer(text='Made by dark#9999 | {}'.format(timestamp), icon_url=footImg)
                                if configData['world']['webhookEnabled?'] == True:
                                    worldHook.send(embed=embed)
                                print("New country found: " + country["attributes"]["Country_Region"])
                        except:
                            print("An error occured. Make sure that the information in your config is correct! (world)")
                        writeWorld(worldData)
                    writeWorld(worldData)
                    #Looks for new data
                    for country in rawWorldData["features"]:
                        try:
                            countryReg = worldData[country["attributes"]["Country_Region"]]
                            timestamp = datetime.now(pytz.timezone("America/New_York")).strftime("%I:%M:%S %p %Z")
                            if country["attributes"]["Deaths"] != countryReg["deaths"]:
                                dataUpdated = True
                                if country["attributes"]["Deaths"] - countryReg["deaths"] < 0:
                                    description = "Case(s) possibly removed from database 💀"
                                    sign = ""
                                else:
                                    description = "New Coronavirus death 💀"
                                    sign = "+"
                                embed = Embed(color=16523049, title=country["attributes"]["Country_Region"], description=description)
                                embed.add_field(name="Update (Deaths)", value="`({}{}) | {} => {}`".format(sign, country["attributes"]["Deaths"] - countryReg["deaths"], countryReg["deaths"], country["attributes"]["Deaths"]), inline=False)
                                countryReg["deaths"] = country["attributes"]["Deaths"]
                                print("Update (Deaths): ({}{}) | {} => {}".format(sign, country["attributes"]["Deaths"] - countryReg["deaths"], countryReg["deaths"], country["attributes"]["Deaths"]))
                            if country["attributes"]["Recovered"] != countryReg["recovered"]:
                                dataUpdated = True
                                if country["attributes"]["Recovered"] - countryReg["recovered"] < 0:
                                    description = "Case(s) possibly removed from database 🥳"
                                    sign = ""
                                else:
                                    description = "Successful Coronavirus recovery 🥳"
                                    sign = "+"
                                embed = Embed(color=718692, title=country["attributes"]["Country_Region"], description=description)
                                embed.add_field(name="Update (Recovered)", value="`({}{}) | {} => {}`".format(sign, country["attributes"]["Recovered"] - countryReg["recovered"], countryReg["recovered"], country["attributes"]["Recovered"]), inline=False)
                                countryReg["recovered"] = country["attributes"]["Recovered"]
                                print("Update (Recovered): ({}{}) | {} => {}".format(sign, country["attributes"]["Recovered"] - countryReg["recovered"], countryReg["recovered"], country["attributes"]["Recovered"]))
                            if country["attributes"]["Confirmed"] != countryReg["confirmed"]:
                                dataUpdated = True
                                if country["attributes"]["Confirmed"] - countryReg["confirmed"] < 0:
                                    description = "Case(s) possibly removed from database ⚠️"
                                    sign = ""
                                else:
                                    description = "New case(s) of Coronavirus ⚠️"
                                    sign = "+"
                                embed = Embed(color=6638321, title=country["attributes"]["Country_Region"], description=description)
                                embed.add_field(name="Update (Confirmed)", value="`({}{}) | {} => {}`".format(sign, country["attributes"]["Confirmed"] - countryReg["confirmed"], countryReg["confirmed"], country["attributes"]["Confirmed"]), inline=False)
                                countryReg["confirmed"] = country["attributes"]["Confirmed"]
                                print("Update (Confirmed): ({}{}) | {} => {}".format(sign, country["attributes"]["Confirmed"] - countryReg["confirmed"], countryReg["confirmed"], country["attributes"]["Confirmed"]))
                            if dataUpdated == True:
                                embed.add_field(name="Total Deaths", value="`{} | {:,}%`".format(country["attributes"]["Deaths"], round(country["attributes"]["Deaths"]/country["attributes"]["Confirmed"]*100, 2)), inline=True)
                                embed.add_field(name="Total Recovered", value="`{} | {:,}%`".format(country["attributes"]["Recovered"], round(country["attributes"]["Recovered"]/country["attributes"]["Confirmed"]*100, 2)), inline=True)
                                embed.add_field(name="Confirmed", value="`{}`".format(country["attributes"]["Confirmed"]), inline=True)
                                embed.set_footer(text='Made by dark#9999 | {}'.format(timestamp), icon_url=footImg)
                                if configData['world']['webhookEnabled?'] == True:
                                    worldHook.send(embed=embed)
                            dataUpdated = False
                        except:
                            print("An error occured. Make sure that the information in your config is correct! (world)")
                        writeWorld(worldData)
                    writeWorld(worldData)
                    #Sends graph on the hour
                    if configData['graphs']['hourly']['enabled?'] == True:
                        if datetime.now(pytz.timezone("America/New_York")).strftime("%M") == "00":
                            countriesInt = []
                            countriesF = {}
                            countries = []
                            confNum = []
                            colors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple', 'tab:brown', 'tab:pink', 'tab:gray', 'tab:olive', 'tab:cyan']

                            for country in rawWorldData["features"]:
                                countriesInt.append({"country": country["attributes"]["Country_Region"], "confirmed": country["attributes"]["Confirmed"]})
                            countriesSorted = sorted(countriesInt, key=lambda x:x["confirmed"], reverse=True)
                            for i in range(15):
                                countriesF[countriesSorted[i]['country']] = countriesSorted[i]["confirmed"]
                                countries.append(countriesSorted[i]['country'])
                                confNum.append(countriesSorted[i]["confirmed"])

                            ind = np.arange(len(countries))
                            plt.barh(ind, confNum, align='center', color=colors, label=True)
                            plt.xlabel('Total Confirmed Cases', fontweight='bold')
                            plt.ylabel('Countries', fontweight='bold')
                            plt.yticks(ind, countries, rotation=30)
                            for i, v in enumerate(confNum):
                                plt.text(v + 3, i, str(round(v, 2)), color='black', va='center', fontweight='bold')
                            plt.tight_layout()

                            chart_dir = os.path.dirname(__file__)
                            resultsDir = os.path.join(chart_dir, 'bar_charts/')
                            chartFileName = "bar_chart." + datetime.now(pytz.timezone("America/New_York")).strftime("%m_%d_%y") + ".png"
                            plt.savefig(resultsDir + chartFileName)
                            plt.clf()

                            CLIENT_ID = configData['imgurClientID']
                            PATH = resultsDir + chartFileName
                            im = pyimgur.Imgur(CLIENT_ID)
                            timeS = datetime.now(pytz.timezone("America/New_York")).strftime("%I%p %Z %x")
                            uploadedImage = im.upload_image(PATH, title="New Chart For: {}".format(time))
                            
                            totalConf = 0
                            totalDeaths = 0
                            for country in rawWorldData["features"]:
                                totalConf = totalConf + country["attributes"]["Confirmed"]
                                totalDeaths = totalDeaths + country["attributes"]["Deaths"]

                            embed = Embed(color=16544031, title=timeS, description=f"**Total Deaths:** {totalDeaths}\n**Total Confirmed:** {totalConf}")
                            embed.set_image(url=uploadedImage.link)
                            embed.set_footer(text='Made by dark#9999 | {}'.format(timestamp), icon_url=footImg)
                            graph.send(embed=embed)
                            waitTime = 62-int(datetime.now(pytz.timezone("America/New_York")).strftime("%S"))
                            time.sleep(waitTime)
                        else:
                            pass
            if configData['unitedStates']['enabled?'] == True: 
                with open('usData.json') as json_file:
                    usData = json.load(json_file)
                    states = list(usData)
                    for county in rawUSData["features"]:
                        try:
                            if county["attributes"]["Province_State"] in states:
                                pass
                            else:
                                usData[county["attributes"]["Province_State"]] = {
                                    "deaths":county["attributes"]["Deaths"],
                                    "recovered":county["attributes"]["Recovered"],
                                    "confirmed":county["attributes"]["Confirmed"]
                                }
                                timestamp = datetime.now(pytz.timezone("America/New_York")).strftime("%I:%M:%S %p %Z")
                                embed = Embed(color=16544031, title=county["attributes"]["Country_Region"], description="New state found 📰")
                                embed.add_field(name="Total Deaths", value="`{} | {:,}%`".format(county["attributes"]["Deaths"], round(county["attributes"]["Deaths"]/county["attributes"]["Confirmed"]*100, 2)), inline=True)
                                embed.add_field(name="Total Recovered", value="`{} | {:,}%`".format(county["attributes"]["Recovered"], round(county["attributes"]["Recovered"]/county["attributes"]["Confirmed"]*100, 2)), inline=True)
                                embed.add_field(name="Confirmed", value="`{}`".format(county["attributes"]["Confirmed"]), inline=True)
                                embed.set_footer(text='Made by dark#9999 | {}'.format(timestamp), icon_url=footImg)
                                if configData['unitedStates']['webhookEnabled?'] == True:
                                    usHook.send(embed=embed)
                                print("New state found: " + county["attributes"]["Country_Region"])
                        except:
                            print("An error occured. Make sure that the information in your config is correct! (unitedStates)")
                        writeUS(usData)
                    writeUS(usData)
                    for county in rawUSData["features"]:
                        try:
                            provState = usData[county["attributes"]["Province_State"]]
                            timestamp = datetime.now(pytz.timezone("America/New_York")).strftime("%I:%M:%S %p %Z")
                            if county["attributes"]["Deaths"] != provState["deaths"]:
                                dataUpdated = True
                                if county["attributes"]["Deaths"] - provState["deaths"] < 0:
                                    description = "Case(s) possibly removed from database 💀"
                                    sign = ""
                                else:
                                    description = "New Coronavirus death 💀"
                                    sign = "+"
                                embed = Embed(color=16523049, title=county["attributes"]["Province_State"], description=description)
                                embed.add_field(name="Update (Deaths)", value="`({}{}) | {} => {}`".format(sign, county["attributes"]["Deaths"] - provState["deaths"], provState["deaths"], county["attributes"]["Deaths"]), inline=False)
                                provState["deaths"] = county["attributes"]["Deaths"]
                                print("Update (Deaths): ({}{}) | {} => {}".format(sign, county["attributes"]["Deaths"] - provState["deaths"], provState["deaths"], county["attributes"]["Deaths"]))
                            if county["attributes"]["Recovered"] != provState["recovered"]:
                                dataUpdated = True
                                if county["attributes"]["Recovered"] - provState["recovered"] < 0:
                                    description = "Case(s) possibly removed from database 🥳"
                                    sign = ""
                                else:
                                    description = "Successful Coronavirus recovery 🥳"
                                    sign = "+"
                                embed = Embed(color=718692, title=county["attributes"]["Province_State"], description=description)
                                embed.add_field(name="Update (Recovered)", value="`({}{}) | {} => {}`".format(sign, county["attributes"]["Recovered"] - provState["recovered"], provState["recovered"], county["attributes"]["Recovered"]), inline=False)
                                provState["recovered"] = county["attributes"]["Recovered"]
                                print("Update (Recovered): ({}{}) | {} => {}".format(sign, county["attributes"]["Recovered"] - provState["recovered"], provState["recovered"], county["attributes"]["Recovered"]))
                            if county["attributes"]["Confirmed"] != provState["confirmed"]:
                                dataUpdated = True
                                if county["attributes"]["Confirmed"] - provState["confirmed"] < 0:
                                    description = "Case(s) possibly removed from database ⚠️"
                                    sign = ""
                                else:
                                    description = "New case(s) of Coronavirus ⚠️"
                                    sign = "+"
                                embed = Embed(color=6638321, title=county["attributes"]["Province_State"], description=description)
                                embed.add_field(name="Update (Confirmed)", value="`({}{}) | {} => {}`".format(sign, county["attributes"]["Confirmed"] - provState["confirmed"], provState["confirmed"], county["attributes"]["Confirmed"]), inline=False)
                                provState["confirmed"] = county["attributes"]["Confirmed"]
                                print("Update (Confirmed): ({}{}) | {} => {}".format(sign, county["attributes"]["Confirmed"] - provState["confirmed"], provState["confirmed"], county["attributes"]["Confirmed"]))
                            if dataUpdated == True:
                                embed.add_field(name="Total Deaths", value="`{} | {:,}%`".format(county["attributes"]["Deaths"], round(county["attributes"]["Deaths"]/county["attributes"]["Confirmed"]*100, 2)), inline=True)
                                embed.add_field(name="Total Recovered", value="`{} | {:,}%`".format(county["attributes"]["Recovered"], round(county["attributes"]["Recovered"]/county["attributes"]["Confirmed"]*100, 2)), inline=True)
                                embed.add_field(name="Confirmed", value="`{}`".format(county["attributes"]["Confirmed"]), inline=True)
                                embed.set_footer(text='Made by dark#9999 | {}'.format(timestamp), icon_url=footImg)
                                if configData['unitedStates']['webhookEnabled?'] == True:
                                    usHook.send(embed=embed)
                                dataUpdated = False
                        except:
                            print("An error occured. Make sure that the information in your config is correct! (unitedStates)")
                        writeUS(usData)
                    writeUS(usData)
            if configData['usSpecific']['enabled?'] == True: 
                with open('usSpecData.json') as json_file:
                    usSpecData = json.load(json_file)
                    counties = list(usSpecData)
                    for county in rawUsSpecData["features"]:
                        try:
                            if county["attributes"]["Combined_Key"] in counties:
                                pass
                            else:
                                usSpecData[county["attributes"]["Combined_Key"]] = {
                                    "deaths":county["attributes"]["Deaths"],
                                    "recovered":county["attributes"]["Recovered"],
                                    "confirmed":county["attributes"]["Confirmed"]
                                }
                                timestamp = datetime.now(pytz.timezone("America/New_York")).strftime("%I:%M:%S %p %Z")
                                embed = Embed(color=16544031, title=county["attributes"]["Combined_Key"], description="New county found 📰")
                                embed.add_field(name="Total Deaths", value="`{} | {:,}%`".format(county["attributes"]["Deaths"], round(county["attributes"]["Deaths"]/county["attributes"]["Confirmed"]*100, 2)), inline=True)
                                embed.add_field(name="Total Recovered", value="`{} | {:,}%`".format(county["attributes"]["Recovered"], round(county["attributes"]["Recovered"]/county["attributes"]["Confirmed"]*100, 2)), inline=True)
                                embed.add_field(name="Confirmed", value="`{}`".format(county["attributes"]["Confirmed"]), inline=True)
                                embed.set_footer(text='Made by dark#9999 | {}'.format(timestamp), icon_url=footImg)
                                if configData['usSpecific']['webhookEnabled?'] == True:
                                    usSpecHook.send(embed=embed)
                                print("New county found: " + county["attributes"]["Combined_Key"])
                        except:
                            print("An error occured. Make sure that the information in your config is correct! (usSpecific)")
                        writeSpecUS(usSpecData)
                    writeSpecUS(usSpecData)
                    for county in rawUsSpecData["features"]:
                        try:
                            provState = usSpecData[county["attributes"]["Combined_Key"]]
                            timestamp = datetime.now(pytz.timezone("America/New_York")).strftime("%I:%M:%S %p %Z")
                            if county["attributes"]["Deaths"] != provState["deaths"]:
                                dataUpdated = True
                                if county["attributes"]["Deaths"] - provState["deaths"] < 0:
                                    description = "Case(s) possibly removed from database 💀"
                                    sign = ""
                                else:
                                    description = "New Coronavirus death 💀"
                                    sign = "+"
                                embed = Embed(color=16523049, title=county["attributes"]["Combined_Key"], description=description)
                                embed.add_field(name="Update (Deaths)", value="`({}{}) | {} => {}`".format(sign, county["attributes"]["Deaths"] - provState["deaths"], provState["deaths"], county["attributes"]["Deaths"]), inline=False)
                                provState["deaths"] = county["attributes"]["Deaths"]
                                print("Update (Deaths): ({}{}) | {} => {}".format(sign, county["attributes"]["Deaths"] - provState["deaths"], provState["deaths"], county["attributes"]["Deaths"]))
                            if county["attributes"]["Recovered"] != provState["recovered"]:
                                dataUpdated = True
                                if county["attributes"]["Recovered"] - provState["recovered"] < 0:
                                    description = "Case(s) possibly removed from database 🥳"
                                    sign = ""
                                else:
                                    description = "Successful Coronavirus recovery 🥳"
                                    sign = "+"
                                embed = Embed(color=718692, title=county["attributes"]["Combined_Key"], description=description)
                                embed.add_field(name="Update (Recovered)", value="`({}{}) | {} => {}`".format(sign, county["attributes"]["Recovered"] - provState["recovered"], provState["recovered"], county["attributes"]["Recovered"]), inline=False)
                                provState["recovered"] = county["attributes"]["Recovered"]
                                print("Update (Recovered): ({}{}) | {} => {}".format(sign, county["attributes"]["Recovered"] - provState["recovered"], provState["recovered"], county["attributes"]["Recovered"]))
                            if county["attributes"]["Confirmed"] != provState["confirmed"]:
                                dataUpdated = True
                                if county["attributes"]["Confirmed"] - provState["confirmed"] < 0:
                                    description = "Case(s) possibly removed from database ⚠️"
                                    sign = ""
                                else:
                                    description = "New case(s) of Coronavirus ⚠️"
                                    sign = "+"
                                embed = Embed(color=6638321, title=county["attributes"]["Combined_Key"], description=description)
                                embed.add_field(name="Update (Confirmed)", value="`({}{}) | {} => {}`".format(sign, county["attributes"]["Confirmed"] - provState["confirmed"], provState["confirmed"], county["attributes"]["Confirmed"]), inline=False)
                                provState["confirmed"] = county["attributes"]["Confirmed"]
                            if dataUpdated == True:
                                embed.add_field(name="Total Deaths", value="`{} | {:,}%`".format(county["attributes"]["Deaths"], round(county["attributes"]["Deaths"]/county["attributes"]["Confirmed"]*100, 2)), inline=True)
                                embed.add_field(name="Total Recovered", value="`{} | {:,}%`".format(county["attributes"]["Recovered"], round(county["attributes"]["Recovered"]/county["attributes"]["Confirmed"]*100, 2)), inline=True)
                                embed.add_field(name="Confirmed", value="`{}`".format(county["attributes"]["Confirmed"]), inline=True)
                                embed.set_footer(text='Made by dark#9999 | {}'.format(timestamp), icon_url=footImg)
                                if configData['usSpecific']['webhookEnabled?'] == True:
                                    usSpecHook.send(embed=embed)
                                dataUpdated = False
                        except:
                            print("An error occured. Make sure that the information in your config is correct! (usSpecific)")
                        writeSpecUS(usSpecData)
                    writeSpecUS(usSpecData)
            
            
            
            
            if configData['graphs']['daily']['enabled?'] == True:
                if datetime.now(pytz.timezone("America/New_York")).strftime("%H:%M") == "00:05" and int(datetime.now(pytz.timezone("America/New_York")).strftime("%S")) < 5:
                    updateUrl = "https://services9.arcgis.com/N9p5hsImWXAccRNI/arcgis/rest/services/PmO6oUpJizhI0jM8pu3n/FeatureServer/0/query?f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&orderByFields=Report_Date_String%20asc&outSR=102100&resultOffset=0&resultRecordCount=1000&cacheHint=true&vispogay={}".format(randomString())
                    headers = {
                        "origin": "https://gisanddata.maps.arcgis.com",
                        "referer": "https://gisanddata.maps.arcgis.com/apps/opsdashboard/index.html"
                    }
                    r6 = requests.get(updateUrl, headers=headers)
                    updateData = r6.json()
                    dates = []
                    china = []
                    other = []
                    recovered = []
                    confirmed = []
                    for date in updateData["features"]:
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
                    plt.xlabel('Dates')
                    plt.ylabel('Number of People')
                    plt.legend()
                    plt.grid()
                    plt.tight_layout()

                    chart_dir = os.path.dirname(__file__)
                    resultsDir = os.path.join(chart_dir, 'bar_charts/')
                    chartFileName = "daily_chart." + datetime.now(pytz.timezone("America/New_York")).strftime("%m_%d_%y") + ".png"
                    plt.savefig(resultsDir + chartFileName)
                    plt.clf()

                    CLIENT_ID = configData['imgurClientID']
                    PATH = resultsDir + chartFileName
                    im = pyimgur.Imgur(CLIENT_ID)
                    timeS = datetime.now(pytz.timezone("America/New_York")).strftime("%x")
                    uploadedImage = im.upload_image(PATH, title="New Chart For: {}".format(time))
                    
                    totalConf = 0
                    totalDeaths = 0
                    for country in rawWorldData["features"]:
                        totalConf = totalConf + country["attributes"]["Confirmed"]
                        totalDeaths = totalDeaths + country["attributes"]["Deaths"]

                    embed = Embed(color=16544031, title=timeS, description=f"**Total Deaths:** {totalDeaths}\n**Total Confirmed:** {totalConf}")
                    embed.set_image(url=uploadedImage.link)
                    embed.set_footer(text='Made by dark#9999 | {}'.format(timestamp), icon_url=footImg)
                    dailyGraph.send(embed=embed)
                    waitTime = 62-int(datetime.now(pytz.timezone("America/New_York")).strftime("%S"))
                    time.sleep(waitTime)


            print("Updated! Waiting {} seconds...".format(refreshInterval))
            time.sleep(int(refreshInterval))
        except:
            print("-----Stopping Monitor-----")
            print("------Clearing files------")
            with open('usSpecData.json') as json_file:
                usSpecData = json.load(json_file)
            usSpecData = {}
            writeSpecUS(usSpecData)
            print("usSpecData:         Done")
            with open('worldData.json') as json_file:
                worldData = json.load(json_file)
            worldData = {}
            writeWorld(worldData)
            print("world:              Done")
            with open('usData.json') as json_file:
                usData = json.load(json_file)
            usData = {}
            writeUS(usData)
            print("unitedStates:       Done")
            sys.exit()

    print("Stopping... 'monitor' set to false")

def checkOld():
    """
    Log pre-existing data
    """
    r1 = requests.get(worldUrl)
    rawWorldData1 = r1.json()
    with open('worldData.json') as json_file:
        worldData = json.load(json_file)

        for country in rawWorldData1["features"]:
            worldData[country["attributes"]["Country_Region"]] = {
                "deaths":country["attributes"]["Deaths"],
                "recovered":country["attributes"]["Recovered"],
                "confirmed":country["attributes"]["Confirmed"]
            }
        writeWorld(worldData)
        print("world:              Done")
    r2 = requests.get(usUrl)
    rawUsData1 = r2.json()
    with open('usData.json') as json_file:
        usData = json.load(json_file)
        for county in rawUsData1["features"]:
            usData[county["attributes"]["Province_State"]] = {
                "deaths":county["attributes"]["Deaths"],
                "recovered":county["attributes"]["Recovered"],
                "confirmed":county["attributes"]["Confirmed"]
            }
        writeUS(usData)
        print("unitedStates:       Done")
    headers = {
        "origin": "https://gisanddata.maps.arcgis.com",
        "referer": "https://gisanddata.maps.arcgis.com/apps/opsdashboard/index.html"
    }
    r0 = requests.get(usSpecUrl, headers=headers)
    rawUsSpecData1 = r0.json()
    with open('usSpecData.json') as json_file:
        usSpecData = json.load(json_file)
        for county in rawUsSpecData1["features"]:
            usSpecData[county["attributes"]["Combined_Key"]] = {
                "deaths":county["attributes"]["Deaths"],
                "recovered":county["attributes"]["Recovered"],
                "confirmed":county["attributes"]["Confirmed"]
            }
        writeSpecUS(usSpecData)
        print("usSpecific:         Done")

def writeWorld(data, filename='worldData.json'):
    with open(filename,'w') as f:
        json.dump(data, f, indent=4) 
def writeUS(data, filename='usData.json'): 
    with open(filename,'w') as f: 
        json.dump(data, f, indent=4)
def writeSpecUS(data, filename='usSpecData.json'): 
    with open(filename,'w') as f: 
        json.dump(data, f, indent=4)
def writeRecent(data, filename='recentData.json'): 
    with open(filename,'w') as f: 
        json.dump(data, f, indent=4)
def randomString(stringLength=10):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))

if __name__ == "__main__":
    print("--Starting Covid Monitor--")
    with open('config.json') as json_file:
        configData = json.load(json_file)
    print("----------Config----------")
    print("unitedStates:       {}".format(configData['unitedStates']['enabled?']))
    #US Sets
    usUrl = "https://services1.arcgis.com/0MSEUqKaxRlEPj5g/arcgis/rest/services/ncov_cases/FeatureServer/1/query?f=json&where=(Confirmed%20%3E%200)%20AND%20(Country_Region%3D%27US%27)&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&orderByFields=Confirmed%20desc%2CCountry_Region%20asc%2CProvince_State%20asc&outSR=102100&resultOffset=0&resultRecordCount=250&cacheHint=true&vispogay={}".format(randomString())
    usHook = Webhook(configData['unitedStates']['webhook'])
    print("world:              {}".format(configData['world']['enabled?']))
    #World Sets
    worldUrl = "https://services1.arcgis.com/0MSEUqKaxRlEPj5g/arcgis/rest/services/ncov_cases/FeatureServer/2/query?f=json&where=Confirmed%20%3E%200&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&orderByFields=Confirmed%20desc&resultOffset=0&resultRecordCount=100&cacheHint=true&vispogay={}".format(randomString())
    worldHook = Webhook(configData['world']['webhook'])
    print("usSpecific:         {}".format(configData['usSpecific']['enabled?']))
    #US Specific Sets
    usSpecUrl = "https://services9.arcgis.com/N9p5hsImWXAccRNI/arcgis/rest/services/Nc2JKvYFoAEOFCG5JSI6/FeatureServer/1/query?f=json&where=Country_Region%3D%27US%27&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&orderByFields=Confirmed%20desc%2CCountry_Region%20asc%2CProvince_State%20asc&outSR=102100&resultOffset=0&resultRecordCount=200&cacheHint=true&vispogay={}".format(randomString())
    usSpecHook = Webhook(configData['usSpecific']['webhook'])
    print("dailyGraphs:        {}".format(configData['graphs']['daily']['enabled?']))
    print("hourlyGraphs:       {}".format(configData['graphs']['hourly']['enabled?']))
    #Misc
    graph = Webhook(configData['graphs']['hourly']['webhook'])
    dailyGraph = Webhook(configData['graphs']['daily']['webhook'])
    footImg = "https://cdn.discordapp.com/attachments/681351512563384400/686349220243963996/dark_phineas_copy.png"
    print("-------Add Old Data-------")
    checkOld()
    print("-----Starting Monitor-----")
    covidMonitor(configData['refreshInterval'])
