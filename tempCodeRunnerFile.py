            dpg.add_input_float(tag = "latInput",label = "Latitude", use_internal_label = True, width = dpg.get_item_height("searchChild"))
            dpg.add_input_float(tag = "longInput",label = "Longitude", use_internal_label = True, width = dpg.get_item_height("searchChild"))
            dpg.add_button(label = "Search", callback = searchLoc)