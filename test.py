import os
import sys
import numpy as np
import pickle
import json
from pyart.core import cartesian_to_geographic as ctg
from mpl_toolkits.basemap import Basemap
from matplotlib.patches import Polygon
import matplotlib.pyplot as plt
sys.path.append('concavehull')
import ConcaveHull as CHull
from sklearn.cluster import DBSCAN
from shapely import geometry
import geopandas
import mysql.connector
from datetime import datetime
import math
import glob
files = glob.glob('/home/dopplerdat/aitews')
print(files)
print('tatek')


# import os
# files = os.listdir("C:/Users/User/Desktop/ai-tews-py-scripts/files")

# with open('logs.txt', 'r+') as logfile:
#     if not files[3] in logfile.read():
#         print('wala pa')
#         logfile.write(files[3] + '\n')
#     else:
#         print('meron na')