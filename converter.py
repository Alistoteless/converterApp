import os
import json
import pyproj
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(BASE_DIR, 'templates', 'epsg.json')


def get_epsg_code(coord_type):
    with open(file_path, 'r') as f:
        data = json.load(f)
    for system in data:
        if system['name'] == coord_type:
            epsg_code = system['EPSG']
    
    return epsg_code

def convert_coordinate(x, y, source_epsg_code, target_epsg_code):
    proj = pyproj.Transformer.from_crs(f"epsg:{source_epsg_code}", f"epsg:{target_epsg_code}")
    lat, lon = proj.transform(x, y)
    return lat, lon