import numpy as np;
import pandas as pd;
import dearpygui.dearpygui as dpg

pd.set_option("mode.copy_on_write", True)

# makes lines in order: red,green,blue,brown,purple,pink,orange
stations_df = pd.read_csv("CTAStops.csv")

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

# tries to find the index of a station using it's name, longitude, and latitude
def stationToDFIndex(station):
    index = stations_df.loc[(stations_df['Name'] == station.name) & (stations_df['Latitude'] == station.lat) & (stations_df['Longitude'] == station.long)].index[0]
    return index

# deletes the station at the given index
def deleteStation(index):
    if index < len(stations_df.index):
        stations_df.drop(index, inplace = True)
        stations_df.reset_index(drop = True, inplace = True)

# searching methods

# returns the closest station given a pair of floats
def stationByCoords(lat,long):
     nearest = stations_df.copy()
     nearest = nearest.iloc[(nearest['Latitude'] - lat).abs().argsort()[:5]]
     nearest = nearest.iloc[(nearest['Longitude'] - long).abs().argsort()[:5]]
     return nearest.iloc[0]

# returns all stations on a line such that their position is not '-1' for that line
def stationsOnLine(line):
     match line.lower():
          case 'red':
               return stations_df.loc[stations_df['Red'] >= 0].reset_index(drop = True)
          case 'green':
               return stations_df.loc[stations_df['Green'] >= 0].reset_index(drop = True)
          case 'blue':
               return stations_df.loc[stations_df['Blue'] >= 0].reset_index(drop = True)
          case 'brown':
               return stations_df.loc[stations_df['Brown'] >= 0].reset_index(drop = True)
          case 'purple':
               return stations_df.loc[stations_df['Purple'] >= 0].reset_index(drop = True)
          case 'pink':
               return stations_df.loc[stations_df['Pink'] >= 0].reset_index(drop = True)
          case 'orange':
               return stations_df.loc[stations_df['Orange'] >= 0].reset_index(drop = True)

# returns all stations with a name
def stationByName(name):
     return stations_df.loc[stations_df["Name"].str.lower() == name.lower()].reset_index(drop = True)


# returns all stations with a given station description
def stationByType(type):
     return stations_df.loc[stations_df["Type"].str.lower() == type.lower()].reset_index(drop = True)

def stationByWheelChair(wc):
     return stations_df.loc[stations_df["Accessibility"] == wc].reset_index(drop = True)


# save current stations_df as CSV to load on reboot
def saveStations():
    file = open("CTAStops.csv", "w")
    columnNames = str(list(stations_df.columns.values))
    columnNames = columnNames.strip('[]')
    columnNames = columnNames.replace('\'',"").replace(" ","")
    file.write(columnNames + "\n")
    for index, row in stations_df.iterrows():
        string = str(list(row)).strip('[]') + "\n"
        string = string.replace("\'","").replace(" ","")
        file.write(string)
    file.close()

def searchLinePrompt():
    if dpg.does_alias_exist("LineInput"):
        dpg.remove_alias("LineInput")
        dpg.remove_alias("SearchLineButton")
        dpg.remove_alias("Line Handler")
    with dpg.window(label = "Searching By Line", width = 200, height = 100, pos = (100,100), on_close = deleteResults):
        dpg.add_text("Line: ")
        dpg.add_input_text(tag = "LineInput", width = 100)
        dpg.add_button(label = "Search", tag = "SearchLineButton")
    with dpg.item_handler_registry(tag = "Line Handler") as handler:
        dpg.add_item_clicked_handler(callback = searchLine)
    dpg.bind_item_handler_registry("SearchLineButton", "Line Handler")

def searchLine():
    search_df = stationsOnLine(dpg.get_value("LineInput"))
    generateSearchWindow(search_df)

def deleteResults():
    if dpg.does_item_exist("results"):
        dpg.delete_item("results")

def searchTypePrompt():
    numTypes = stations_df['Type'].unique().tolist()
    if dpg.does_alias_exist("TypeInput"):
        dpg.remove_alias("TypeInput")
        dpg.remove_alias("SearchTypeButton")
        dpg.remove_alias("Type Handler")
    with dpg.window(label = "Searching By Station Description", width = 275, height = 150, pos = (25,100), on_close = deleteResults) as typeWindow:
        dpg.add_text("Type: ")
        dpg.add_listbox(numTypes,num_items = 4,tag = "TypeInput")
        dpg.add_button(label = "Search", tag = "SearchTypeButton")
    with dpg.item_handler_registry(tag = "Type Handler") as handler:
        dpg.add_item_clicked_handler(callback = searchType)
    dpg.bind_item_handler_registry("SearchTypeButton", "Type Handler")
    

def searchType():
    search_df = stationByType(dpg.get_value("TypeInput"))
    generateSearchWindow(search_df)

def generateSearchWindow(search_df):
    if dpg.does_item_exist("results"):
        dpg.delete_item("results")
    if search_df is not None:
        columnNames = search_df.columns.values.tolist()
        with dpg.window(pos = (300,100), tag = "results"):
            with dpg.table(header_row=True, resizable=True, policy=dpg.mvTable_SizingStretchProp,
                            borders_outerH=True, borders_innerV=True, borders_innerH=True, borders_outerV=True):
                for i in columnNames:
                    dpg.add_table_column(label = i)
                for i in range(0,search_df.shape[0]):
                    with dpg.table_row():
                        row_list = search_df.loc[i, :].values.flatten().tolist()
                        for j in row_list:
                            with dpg.table_cell():
                                dpg.add_button(label = j)
    else:
        with dpg.window(pos = (300,100), tag = "results"):
            dpg.add_text("Sorry, there were no stations found")
    

dpg.create_context()
dpg.create_viewport(title='CTA Project', width=1280, height=720)
dpg.set_viewport_vsync(True)

with dpg.window(tag = "Main"):
    with dpg.menu_bar():
        with dpg.menu(label = "Search"):
            dpg.add_menu_item(label = "On A Line", callback = searchLinePrompt)
            dpg.add_menu_item(label = "Station Description", callback = searchTypePrompt)

dpg.set_exit_callback(callback = saveStations())
dpg.set_primary_window("Main",True)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
