import numpy as np;
import pandas as pd;
import dearpygui.dearpygui as dpg

pd.set_option("mode.copy_on_write", True)

# makes lines in order: red,green,blue,brown,purple,pink,orange
stations_df = pd.read_csv("project/CTAStops.csv")

# Station class, manages each station a little bit easier
class Station:
    def __init__(self,name = "None", lat = -1, long  = -1, type = "None", wc = False, lines = [0,0,0,0,0,0,0]):
        self.name = name
        self.lat = lat
        self.long = long
        self.type = type
        self.wc = wc
        self.lines = lines

    def __str__(self):
        return "Name: %s, Lat: %f, Long: %f, Type: %s, Accessible: %s, \nRed Line: %d, Green Line: %d, Blue Line: %d, Brown Line: %d, Purple Line: %d, Pink Line: %d, Orange Line: %d" %(self.name, self.lat, self.long,
                                                                                                                                                                                       self.type,self.wc, self.lines[0],
                                                                                                                                                                                       self.lines[1],self.lines[2],self.lines[3],
                                                                                                                                                                                       self.lines[4],self.lines[5],self.lines[6])

# modify the station at a given index
def modifyStation(index, name, lat, long, type, wc, lines):
     stations_df.iloc[index] = [name, lat, long, type, wc, lines[0],lines[1],lines[2],lines[3],lines[4],lines[5],lines[6]]

# append station to stations_df
def addStation(name, lat, long, type, wc, lines):
    stations_df.loc[len(stations_df.index)] = [name, lat, long, type, wc, lines[0],lines[1],lines[2],lines[3],lines[4],lines[5],lines[6]]

# creates a station object given an index for stations_df
def dfToStation(index):
    dfStation = stations_df.iloc[index]
    stationLines = [dfStation['Red'],dfStation['Green'],dfStation['Blue'], dfStation['Brown'],dfStation['Purple'],dfStation['Pink'],dfStation['Orange']]
    newStation = Station(dfStation['Name'],dfStation['Latitude'],dfStation['Longitude'],dfStation['Type'],dfStation['Accessibility'],stationLines)
    return newStation
