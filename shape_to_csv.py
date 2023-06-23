import os
import sys
import json
import geopandas
import numpy as np
import csv


# with open('municipalities_shapes.csv') as f:
#     print(f)
#     exit()
muni_shapes = geopandas.read_file('shapes/Municipalities_2%_simplified/Municipalities.shp')

def shape_to_csv(shapes, headers, filename):
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        for index, shape in shapes.iterrows():
            region = '"' + shape.ADM1_EN.encode('latin-1').decode('utf-8') + '"'
            province = '"' + shape.ADM2_EN.encode('latin-1').decode('utf-8') + '"'
            municipality = '"' + shape.ADM3_EN.encode('latin-1').decode('utf-8') + '"'
            psgc_code = '"' + shape.ADM3_PCODE[2:].encode('latin-1').decode('utf-8') + '"'
            id = '"' + str(index + 1) + '"'
            print(index)
            if shape.geometry.geom_type == 'MultiPolygon':
                polygon = [[np.column_stack((sg.exterior.coords.xy[1], sg.exterior.coords.xy[0])).tolist()] for sg in shape.geometry.geoms ]
            else:
                polygon = [np.column_stack((shape.geometry.exterior.coords.xy[1], shape.geometry.exterior.coords.xy[0])).tolist()]

            writer.writerow([id, region, province, municipality, psgc_code, '"' + str(polygon) + '"'])

    print('done')

headers = ['id', 'region', 'province', 'municipality', 'psgc_code', 'polygon']

shape_to_csv(muni_shapes, headers, 'municipalities_shapes.csv')


# brgy_shp = geopandas.read_file('shapes/Barangays_2%_simplified/Barangays.shp')

# def shape_to_csv(shapes, headers, filename):
#     with open(filename, 'w', newline='') as csvfile:
#         writer = csv.writer(csvfile)
#         writer.writerow(headers)  # Write the header row
#         for index, shape in shapes.iterrows():
#             region = '"' + shape.ADM1_EN.encode('latin-1').decode('utf-8') + '"'
#             province = '"' + shape.ADM2_EN.encode('latin-1').decode('utf-8') + '"'
#             municipality = '"' + shape.ADM3_EN.encode('latin-1').decode('utf-8') + '"'
#             barangay = '"' + shape.ADM4_EN.encode('latin-1').decode('utf-8') + '"'
#             psgc_code = '"' + shape.ADM4_PCODE[2:].encode('latin-1').decode('utf-8') + '"'
#             id = '"' + str(index + 1) + '"'
#             print(index)
#             if shape.geometry.geom_type == 'MultiPolygon':
#                 polygon = [[np.column_stack((sg.exterior.coords.xy[1], sg.exterior.coords.xy[0])).tolist()] for sg in shape.geometry.geoms ]
#             else:
#                 polygon = [np.column_stack((shape.geometry.exterior.coords.xy[1], shape.geometry.exterior.coords.xy[0])).tolist()]

#             writer.writerow([id, region, province, municipality, barangay, psgc_code, '"' + str(polygon) + '"'])

#     print('done')

# headers = ['id', 'region', 'province', 'municipality', 'barangay', 'psgc_code', 'polygon']

# shape_to_csv(brgy_shp, headers, 'barangay_shapes.csv')

