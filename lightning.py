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

radar_name = sys.argv[1]

path = '/home/dopplerdat/aitews/'

centers = {
    'Subic' : [120.363697916666667, 14.822096354166666],
    'Tagaytay' : [121.02194544119878, 14.141686134603923]
}

barangays = geopandas.read_file('shapes/Barangays01%/Barangays.shp')
municipalities = geopandas.read_file('shapes/Municipalities01%/Municipalities.shp')

current_date = datetime.today()

processed_log_file = "/var/ai-tews/" + str(current_date)[0:10].replace('-','_') + "_processed_logs.txt"

if not os.path.exists(processed_log_file):
    open(processed_log_file, 'w').close()

def save_to_database(output):
    database = mysql.connector.connect(
        host = "localhost",
        user = "root",
        passwd = "password123",
        database = "ai_tews",
    )
    
    cursor = database.cursor()

    sql = "INSERT INTO predictions (radar, type, threshold, datetime, affected_municipalities, affected_barangays, polygons, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    values = (radar_name, 'lightning', output['threshold'], output['datetime'], str(json.dumps(output['affected_municipalities'])),str(json.dumps(output['affected_barangays'])), str(json.dumps(output['polygons'])), str(datetime.now()), str(datetime.now()))
    cursor.execute(sql, values)

    database.commit()
    cursor.close()
    database.close()



def convert_cartesian_to_geographic(cartesian, threshold):
    proj_params = {
        'proj': 'pyart_aeqd',
        'lon_0': centers[radar_name][0],
        'lat_0': centers[radar_name][1]
    }
    cy, cx = np.where(cartesian >= threshold)
    gx, gy = (cx - 128) * 1000, (cy - 128) * 1000

    return ctg(gx, gy, projparams=proj_params)

def get_affected_areas(polygons, shapeType = 'municipality'):
    shapes, affected_areas = municipalities, []

    if shapeType == 'barangay':
        shapes = barangays

    for index, shape in shapes.iterrows():
        area_counter, psgc_code, name = 0, shape.ADM3_PCODE, shape.ADM3_EN

        if shapeType == 'barangay':
            psgc_code = shape.ADM4_PCODE
            name = shape.ADM3_EN
        
        psgc_code = psgc_code.encode('latin-1').decode('utf-8')[2:]
        name = name.encode('latin-1').decode('utf-8')


        if not str(shape.geometry) == 'None':
            for pdex in range(len(polygons)):
                try:
                    polygon = geometry.Polygon(polygons[pdex])
                    if shape.geometry.intersects(polygon):
                        area_counter = area_counter + shape.geometry.intersection(polygon).area   
                except:
                    print('error in polygon')
        
        
        if area_counter > 0:
            coverage = math.ceil(area_counter / shape.geometry.area * 100)
            if coverage > 0:
                if coverage > 100: 
                    coverage = 100

                affected_areas.append({'psgc_code':psgc_code, 'coverage':coverage})

    return affected_areas

def create_polygons(points):
    clusters, polygons, scanned = [], [], DBSCAN(eps=.01).fit(points)


    for label in set(scanned.labels_):
        if label >= 0:
            clusters.append(points[np.where(scanned.labels_ == label)])

    for point in range(len(clusters)):
        if len(clusters[point]) > 1:
            polygon = geometry.Polygon(CHull.concaveHull(clusters[point], 25))
            if polygon.area > .0002:
                polygons.append(polygon)

    return polygons

def generate(filename):
    with open(processed_log_file, 'r+') as processed_logs:
        if not filename in processed_logs.read():
            output, thresholds = {}, [.5, .6, .7, .8, .9 , 1.0]
            file = open(path + filename, 'rb')
            pickle_file = pickle.load(file)
            data = pickle_file.get('predictions')[0]
            output['datetime'] = datetime.fromtimestamp(int(filename.split('_')[2]) - 600 + 28800).strftime('%Y-%m-%d %H:%M')

            for threshold in thresholds:
                output['affected_municipalities'] = []
                output['affected_barangays'] = []
                output['polygons'] = []
                output['threshold'] = threshold
                for index, cartesian in enumerate(data):
                    cartesian = np.reshape(cartesian, (256, 256))
                    glons, glats = convert_cartesian_to_geographic(cartesian, threshold)
                    valid_points = np.column_stack((glons, glats))

                    if(len(valid_points) > 0):
                        hulls = create_polygons(valid_points)
                        lightning_polygons = [ [np.column_stack((hull.exterior.coords.xy[1], hull.exterior.coords.xy[0])).tolist()] for hull in hulls ]
                        output['polygons'].append(lightning_polygons)
                        output['affected_municipalities'].append(get_affected_areas(hulls))
                        output['affected_barangays'].append(get_affected_areas(hulls, 'barangay'))

                save_to_database(output)

            print("Done processing file: " + filename)
            processed_logs.write(filename + "\n")
        else:
            print(filename + " Already Processed!.")


files = glob.glob(path + radar_name.lower()[0:3] + '*')
latest_file = max(files, key = os.path.getctime)

generate(os.path.basename(latest_file))

# filename = 'sub_predictions_1684575010_1684578010.pkl'
# generate('sub_predictions_1687814410_1687817410.pkl')

# path = "C:/Users/User/Desktop/ai-tews-py-scripts/files"
# files = os.listdir(path)
# for filename in files:
#     generate(filename)





