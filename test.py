import os
# import sys
# import numpy as np
# import pickle
# import json
# from pyart.core import cartesian_to_geographic as ctg
# from mpl_toolkits.basemap import Basemap
# from matplotlib.patches import Polygon
# import matplotlib.pyplot as plt
# sys.path.append('concavehull')
# import ConcaveHull as CHull
# from sklearn.cluster import DBSCAN
# from shapely import geometry
# import geopandas
# import mysql.connector
from datetime import datetime
# import math
# import glob
# files = glob.glob('/home/dopplerdat/aitews')

current_date = datetime.today()

processed_log_file = "C:/Users/User/Desktop/ai-tews-py-scripts/" + str(current_date)[0:10].replace('-','_') + "_processed_logs.txt"
if not os.path.exists(processed_log_file):
    open(processed_log_file, 'w').close()
    # open(str("C:/Users/User/Desktop/ai-tews-py-scripts/" + processed_log_file), 'w').close()

# if not os.path.exists("C:/Users/User/Desktop/ai-tews-py-scripts/20230703_processed_logs.txt"):
    # print(str(datetime_today)[0:10].replace("-", "_"))

# import os
# files = os.listdir("C:/Users/User/Desktop/ai-tews-py-scripts/files")

# with open(str("C:/Users/User/Desktop/ai-tews-py-scripts/" + processed_log_file), 'r+') as logfile:
#         logfile.write("pogi")