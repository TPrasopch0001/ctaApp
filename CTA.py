import numpy as np;
import pandas as pd;
import dearpygui.dearpygui as dpg

pd.set_option("mode.copy_on_write", True)

# makes lines in order: red,green,blue,brown,purple,pink,orange
stations_df = pd.read_csv("data/CTAStops.csv")
selectRow = ""
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
     return stations_df[stations_df["Name"].str.contains(name, case = False)].reset_index(drop = True)


# returns all stations with a given station description
def stationByType(type):
     return stations_df.loc[stations_df["Type"].str.lower() == type.lower()].reset_index(drop = True)

def stationByWheelChair(wc):
     return stations_df.loc[stations_df["Accessibility"] == wc].reset_index(drop = True)


# save current stations_df as CSV to load on reboot
def saveStations():
    file = open("data/CTAStops.csv", "w")
    columnNames = str(list(stations_df.columns.values))
    columnNames = columnNames.strip('[]')
    columnNames = columnNames.replace('\'',"").replace(" ","")
    file.write(columnNames + "\n")
    for index, row in stations_df.iterrows():
        string = str(list(row)).strip('[]') + "\n"
        string = string.replace("\'","")
        file.write(string)
    file.close()


dpg.create_context()
dpg.create_viewport(title='CTA Project', width = 1600, height = 900, resizable = False)
dpg.set_viewport_vsync(True)

# additional fonts
with dpg.font_registry():
    defaultFont = dpg.add_font("fonts/Inter-VariableFont_slnt,wght.ttf", 15)
    fontOption1 = dpg.add_font("fonts/NotoSerifCJKjp-Medium.otf", 15)

with dpg.window(tag = "Main", no_scrollbar = True, no_resize = True) as main:
    def selectCallback(sender, app_data, user_data):
        global selectRow
        selectRow = user_data

# Methods for within main window
    def searchLinePrompt():
        if not (dpg.does_item_exist("searchChild")):
            generateNullSearchWindow()
        if dpg.does_alias_exist("lineInput"):
            dpg.remove_alias("lineInput")
        dpg.delete_item("searchChild", children_only = True)
        with dpg.group(parent = "searchChild"):
            dpg.add_text("Line Name: ")
            dpg.add_input_text(tag = "lineInput", width = dpg.get_item_height("searchChild")/4)
            dpg.add_button(label = "Search", tag = "lineSearch")
        with dpg.item_handler_registry() as handler:
            dpg.add_item_clicked_handler(callback = searchLine)
        dpg.bind_item_handler_registry("lineSearch", handler)

    def searchLine():
        dpg.delete_item("resultsChild",children_only = True)
        search_df = stationsOnLine(dpg.get_value("lineInput"))
        generateSearchResultsWindow(search_df)

    def searchTypePrompt():
        if not (dpg.does_item_exist("searchChild")):
            generateNullSearchWindow()
        if dpg.does_alias_exist("typeInput"):
            dpg.remove_alias("typeInput")
            dpg.remove_alias("typeSearch")
            dpg.remove_alias("wcBool")
        numTypes = stations_df['Type'].unique().tolist()
        dpg.delete_item("searchChild", children_only = True)
        with dpg.group(parent = "searchChild", horizontal = True):
            with dpg.group():
                dpg.add_text("Type: ")
                dpg.add_listbox(numTypes,num_items = 4,tag = "typeInput")
                dpg.add_button(label = "Search", tag = "typeSearch")
            with dpg.group():
                dpg.add_text("Wheelchair \nAccessible: ")
                dpg.add_checkbox(tag = "wcBool")
        with dpg.item_handler_registry() as handler:
            dpg.add_item_clicked_handler(callback = searchType)
        dpg.bind_item_handler_registry("typeSearch", handler)


    def searchType():
        dpg.delete_item("resultsChild",children_only = True)
        search_df = stationByType(dpg.get_value("typeInput"))
        if dpg.get_value("wcBool"):
            generateSearchResultsWindow(search_df.loc[search_df['Accessibility'] == True].reset_index(drop = True))
        else:
            generateSearchResultsWindow(search_df)

    def searchNamePrompt():
        if not (dpg.does_item_exist("searchChild")):
            generateNullSearchWindow()
        if dpg.does_alias_exist("nameString"):
            dpg.remove_alias("nameString")
            dpg.remove_alias("nameSearch")
        dpg.delete_item("searchChild", children_only = True)
        with dpg.group(parent = "searchChild"):
            dpg.add_text("Station Name: ")
            dpg.add_input_text(tag = "nameString", width = dpg.get_item_height("searchChild")/3)
            dpg.add_button(label = "Search", tag = "nameSearch")
        with dpg.item_handler_registry() as handler:
            dpg.add_item_clicked_handler(callback = searchText)
        dpg.bind_item_handler_registry("nameSearch", handler)
    
    def searchText():
        dpg.delete_item("resultsChild",children_only = True)
        search_df = stationByName(dpg.get_value("nameString").lower())
        generateSearchResultsWindow(search_df)

    def searchLocPrompt():
        if not (dpg.does_item_exist("searchChild")):
            generateNullSearchWindow()
        if dpg.does_alias_exist("latInput"):
            dpg.remove_alias("latInput")
            dpg.remove_alias("longInput")
        dpg.delete_item("searchChild", children_only = True)
        with dpg.group(parent = "searchChild"):
            dpg.add_text("Latitude: ")
            dpg.add_input_float(tag = "latInput", step = 0)
            dpg.add_text("Longitude: ")
            dpg.add_input_float(tag = "longInput",step = 0)
            dpg.add_button(label = "Search", callback = searchLoc)

    def searchLoc():
        dpg.delete_item("resultsChild",children_only = True)
        lat = dpg.get_value("latInput")
        long = dpg.get_value("longInput")
        search_df = stationByCoords(lat,long)
        generateSingleSearchWindow(search_df)
    
    def generateNullSearchWindow():
        dpg.add_group(parent = main, tag = "mainSearchGroup", horizontal = True)
        dpg.add_child_window(parent = "mainSearchGroup",tag = "searchChild",width = (dpg.get_viewport_width())/4)
        dpg.add_child_window(parent = "mainSearchGroup",tag = "resultsChild")

    def cleanSearches():
        dpg.delete_item("mainSearchGroup")
        dpg.remove_alias("mainSearchGroup")
        
    def generateNullModifyWindow():
        dpg.add_group(parent = main, tag = "mainModGroup", horizontal = True)
        dpg.add_child_window(parent = "mainModGroup",tag = "modChild",width = (dpg.get_viewport_width())/4)
        dpg.add_child_window(parent = "mainModGroup",tag = "resultsChild")
    
    def cleanModWindows():
        dpg.delete_item("mainModGroup")
        dpg.remove_alias("mainModGroup")

# Main Window Items
    with dpg.menu_bar():
        with dpg.menu(label = "Options"):
            dpg.add_menu_item(label = "Preferences")
        with dpg.menu(label = "Search"):
            dpg.add_menu_item(label = "By Name", callback = searchNamePrompt)
            dpg.add_menu_item(label = "By Location", callback = searchLocPrompt)
            dpg.add_menu_item(label = "On A Line", callback = searchLinePrompt)
            dpg.add_menu_item(label = "Station Description", callback = searchTypePrompt)
        with dpg.menu(label = "Modify"):
            dpg.add_menu_item(label = "Add a Station")
            dpg.add_menu_item(label = "Edit a Station")
        dpg.add_menu_item(label = "Path Finding")


# GUI handlers
    def generateSingleSearchWindow(search_df, selectable = False):
        if search_df is not None or not search_df.empty:
            columnNames = stations_df.columns.values.tolist()
            with dpg.table(header_row=True, policy=dpg.mvTable_SizingStretchProp,
                           borders_outerH=True, borders_innerV=True, borders_innerH=True, borders_outerV=True,
                           row_background = True, parent = "resultsChild"):
                    for i in columnNames:
                        dpg.add_table_column(label = i)
                    with dpg.table_row():
                        for j in search_df:
                            if selectable:
                                dpg.add_selectable(label = j, span_columns = True, callback = selectCallback, user_data = search_df)
                            else:
                                dpg.add_text(j)
        else:
            dpg.add_text("Sorry, there were no stations found", parent = "resultsChild")

    def generateSearchResultsWindow(search_df, selectable = False):
        if search_df is not None or not search_df.empty:
            columnNames = search_df.columns.values.tolist()
            with dpg.table(header_row=True, policy=dpg.mvTable_SizingStretchProp,
                           borders_outerH=True, borders_innerV=True, borders_innerH=True, borders_outerV=True,
                           row_background = True, parent = "resultsChild"):
                for i in columnNames:
                    dpg.add_table_column(label = i)
                for i in range(0,search_df.shape[0]):
                    with dpg.table_row():
                        row_list = search_df.loc[i, :].values.flatten().tolist()
                        for j in row_list:
                            with dpg.table_cell():
                                if selectable:
                                    dpg.add_selectable(label = j, span_columns = True, callback = selectCallback, user_data = row_list)
                                else:
                                    dpg.add_text(j)
        else:
            dpg.add_text("Sorry, there were no stations found", parent = "resultsChild")

with dpg.theme() as globalTheme:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (37, 41, 46))
        dpg.add_theme_color(dpg.mvThemeCol_Button, (18, 88, 176))
    with dpg.theme_component(dpg.mvTable):
        dpg.add_theme_color(dpg.mvThemeCol_Header, (41, 128, 185))


dpg.bind_theme(globalTheme)
dpg.bind_font(defaultFont)
# dpg.show_font_manager()
dpg.show_style_editor()
dpg.set_exit_callback(callback = saveStations)
dpg.set_primary_window("Main",True)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
