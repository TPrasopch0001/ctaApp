import numpy as np;
import pandas as pd;
import dearpygui.dearpygui as dpg

pd.set_option("mode.copy_on_write", True)

# makes lines in order: red,green,blue,brown,purple,pink,orange
stations_df = pd.read_csv("project/CTAStops.csv")
