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

14.141686134603923, 121.02194544119878

proj_params = {
    'proj': 'pyart_aeqd',
    #tagatay
    # 'lon_0': 121.02194544119878,
    # 'lat_0':14.141686134603923,
    #subic
    'lon_0': 120.363697916666667,
    'lat_0': 14.822096354166666
} 
map = Basemap(
    resolution='i', 
    area_thresh=1000, 
    llcrnrlon=117.8072, 
    llcrnrlat=12.0612, 
    urcrnrlon=123.7398, 
    urcrnrlat=16.9891,
	projection='lcc',
    lat_1=0,
    lat_2=1,
    lon_0=0,
)

fig = plt.figure(figsize=(7, 7))
ax = fig.add_subplot(1, 1, 1)
ax.set_aspect('auto')
plt.tight_layout()

def draw_polygon( lats, lons, m, color='yellow', zorder=2):
    x, y = m( np.array(lats), np.array(lons))
    xy = zip(x, y)
    poly = Polygon( list(xy), ec='k', color=color, alpha=0.6, zorder=zorder)
    plt.gca().add_patch(poly)

def convert_cartesian_to_geographic_points(cartesian, threshold):
    cartesian_y, cartesian_x = np.where(cartesian >= threshold)
    grid_x, grid_y = (cartesian_x - 128) * 1000, (cartesian_y - 128) * 1000
    return ctg(grid_x, grid_y, projparams=proj_params)

def get_cluster_from_points(cluster, points):
    points_cluster = []
    for label in set(cluster.labels_):
        if label >= 0:
            c_index = np.where(cluster.labels_ == label)
            points_cluster.append(points[c_index])
    return points_cluster

def create_polygon_hulls(cluster_points):
    cluster_hulls = []

    for point in range(len(cluster_points)):
        polygon = geometry.Polygon(CHull.concaveHull(cluster_points[point], 25))
        if polygon.area > .0002:
            cluster_hulls.append(polygon)
    return cluster_hulls

def get_affected_areas(polygons):
    affected_areas = []

    for index, shape in municipality_shapes.iterrows():
        municipality_name = shape.NAME_2.encode('latin1').decode('utf-8')
        province_name = shape.PROVINCE.encode('latin1').decode('utf-8')
        area_ctr = 0

        if 'ñ' in municipality_name.lower():
            municipality_name = municipality_name.replace('ñ', 'n')

        if not str(shape.geometry) == 'None' and 'lake' not in municipality_name.lower():
            for idx in range(len(polygons)):
                try:
                    polygon = geometry.Polygon(polygons[idx])
                    if(shape.geometry.intersects(polygon)):
                        polygon = shape.geometry.intersection(polygon)
                        area_ctr = area_ctr + polygon.area
                except:
                    print('error polygon')

            if(area_ctr > 0):
                # coverage = int(area_ctr / shape.geometry.area * 100)
                coverage = math.ceil(area_ctr / shape.geometry.area * 100)
                if coverage > 100:
                    coverage = 100
                    
                if(coverage > 0):
                    affected_areas.append({'coverage': coverage, 'municipality':municipality_name, 'province': province_name})

                    # if not shape.geometry.geom_type == 'MultiPolygon':
                    #     affected_areas.append({'coverage': coverage, 'municipality':municipality_name, 'province': province_name})
                    #     shape_x, shape_y = shape.geometry.exterior.coords.xy
                        #for plotting affected areas
                        # draw_polygon(shape_x, shape_y, map, 'blue')
                    # else:
                    #     for shape_polygon in shape.geometry:
                    #         shape_x,shape_y = shape_polygon.coords.xy
                            # draw_polygon(shape_x, shape_y, map, 'blue')
                            
    return affected_areas

def generate(data, threshold, radar_name, dt):
    output = [[],[]]
    #SET DIRECTORY
    directory = 'dots/predictions/'

    if not os.path.exists(directory):
        os.makedirs(directory)

    for index, cartesian in enumerate(data):
        affected_areas = []
        lightning_polygons = []
        plt.clf()
        cartesian = np.reshape(cartesian, (256, 256))
        geo_lons, geo_lats = convert_cartesian_to_geographic_points(cartesian, threshold)
        points = np.column_stack((geo_lons, geo_lats))

        #for plotting point data
        # map.drawcoastlines()
        # map.drawcountries()
        # map.drawmapboundary(fill_color='aqua')
        # map.scatter(geo_lons, geo_lats, latlon=True, marker='.', color='yellow')

        if len(points) > 0:
            cluster = DBSCAN(eps=.01).fit(points)
            cluster_points = get_cluster_from_points(cluster, points)
            hulls = create_polygon_hulls(cluster_points)
            affected_areas = get_affected_areas(hulls)

            lightning_polygons = [ [np.column_stack((hull.exterior.coords.xy[1], hull.exterior.coords.xy[0])).tolist()] for hull in hulls ]

            #for plotting lightning polygon
            # for lightning_polygon in hulls:
            #     l_x, l_y = lightning_polygon.exterior.coords.xy
            #     draw_polygon(l_x, l_y, map)

        output[0].append(affected_areas)
        output[1].append(lightning_polygons)

        #for savinng to file
        # plt.xlabel('+' + str((index + 1) * 10) + ' minutes')
        # plt.show()
        # plt.savefig(directory + '/prediction_' + str(index) + '.png')


    aa, lp = output
    # save to database
    database = mysql.connector.connect(
        host = "localhost",
        user = "root",
        passwd = "",
        database = "ai_tews",
    )

    cursor = database.cursor()
    
    sql = "INSERT INTO predictions (name, type, shape,  threshold, datetime, affected_areas, polygons, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    values = (radar_name, 'lightning', 'municipality', str(threshold), dt, str(json.dumps(aa)), str(json.dumps(lp)), str(datetime.now()), str(datetime.now()))
    cursor.execute(sql, values)

    database.commit()
    cursor.close()
    database.close()

    json_object = json.dumps(output, indent=4, ensure_ascii=False)
    with open(directory + "output.json", "w", encoding='utf-8') as outfile:
        outfile.write(json_object)


# file = open('trial.pkl', 'rb')

# pickle_file = pickle.load(file)

# data = pickle_file.get('num0_mem1').get('preds')[:6]
# dt = '2023-05-20 17:10:00'
# file = open('predictions.pkl', 'rb')
file = open('sub_predictions_1686723010_1686726010.pkl', 'rb')


pickle_file = pickle.load(file)
data = pickle_file.get('predictions')[0]

dt = datetime.fromtimestamp(pickle_file.get('timestamps')[0] - 600).strftime('%Y-%m-%d %H:%M')

municipality_shapes = geopandas.read_file('MuniCities/MuniCities.shp')
radar_name = 'Subic'

for threshold in [.5, .6, .7, .8, .9 , 1.0]:
    generate(data, threshold, radar_name, dt)




