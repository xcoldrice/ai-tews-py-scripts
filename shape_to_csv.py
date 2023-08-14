import os
import sys
import json
import geopandas
import numpy as np
import csv

def shape_to_csv(shapes, headers, filename):
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        for index, shape in shapes.iterrows():
            if shape.geometry.geom_type == 'MultiPolygon':
                polygon = [[np.column_stack((sg.exterior.coords.xy[1], sg.exterior.coords.xy[0])).tolist()] for sg in shape.geometry.geoms ]
            else:
                polygon = [np.column_stack((shape.geometry.exterior.coords.xy[1], shape.geometry.exterior.coords.xy[0])).tolist()]

            id = '"' + str(index + 1) + '"'
            region = '"' + shape.ADM1_EN.encode('latin-1').decode('utf-8') + '"'
            province = '"' + shape.ADM2_EN.encode('latin-1').decode('utf-8') + '"'

            if 'province' in filename:
                writer.writerow([
                    id,
                    region,
                    province,
                    '"' + shape.ADM2_PCODE[2:].encode('latin-1').decode('utf-8') + '"',
                    '"' + str(polygon) + '"'
                ])
            elif 'municipality' in filename:
                writer.writerow([
                    id,
                    region,
                    province,
                    '"' + shape.ADM3_EN.encode('latin-1').decode('utf-8') + '"',
                    '"' + shape.ADM3_PCODE[2:].encode('latin-1').decode('utf-8') + '"',
                    '"' + str(polygon) + '"'
                ])
            elif 'barangay' in filename:
                writer.writerow([
                    id,
                    region,
                    province,
                    '"' + shape.ADM3_EN.encode('latin-1').decode('utf-8') + '"',
                    '"' + shape.ADM4_EN.encode('latin-1').decode('utf-8') + '"',
                    '"' + shape.ADM4_PCODE[2:].encode('latin-1').decode('utf-8') + '"',
                    '"' + str(polygon) + '"'
                ])

    print('done')
    
# muni_shapes = geopandas.read_file('shapes/Municipalities01%/Municipalities.shp')
# muni_headers = ['id', 'region', 'province', 'municipality', 'psgc_code', 'polygon']
# shape_to_csv(muni_shapes, muni_headers, 'municipality_shapes.csv')

# prov_shapes = geopandas.read_file('shapes/Provinces01%/Provinces.shp')
# prov_headers = ['id', 'region', 'province', 'psgc_code', 'polygon']
# shape_to_csv(prov_shapes, prov_headers, 'province_shapes.csv')

brgy_shapes = geopandas.read_file('shapes/Barangays01%/Barangays.shp')
brgy_headers = ['id', 'region', 'province', 'municipality', 'barangay', 'psgc_code', 'polygon']
shape_to_csv(brgy_shapes, brgy_headers, 'barangay_shapes.csv')



