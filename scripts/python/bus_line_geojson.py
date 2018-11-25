"""bus_line_scorer.py

Scores each district based on bus lines.
"""

import json
import geojson
from math import log
from shapely.geometry import Point, LineString, asShape

from sp_districts import get_districts, is_line_in_district


_INPUT_FILE = 'data/bus_lines_accessibility.json'
_OUTPUT_FILE = 'data/bus_lines_geo.json'

def get_bus_lines():
    """Returns an object with raw bus lines data.
    """
    with open(_INPUT_FILE,  'r') as f:
        bus_lines_json = json.load(f)

    for bus_line in bus_lines_json:
        # Transforms coordinates to GeoJson standard.
        bus_line['shape'] = LineString(map(lambda pair: (pair['lng'], pair['lat']),
                                bus_line['shape']))
    zonas_json = json.loads("""
    {"type": "FeatureCollection", "features": []}
    """)

    feature = []

    for i in range(0, len (bus_lines_json)):
            feature.append( geojson.Feature(geometry = bus_lines_json[i]['shape'], properties = {'route_id':bus_lines_json[i]['route_id'],'accessibility_score':bus_lines_json[i]['accessibility_score']}))

    zonas_json['features'] = feature
    with open(_OUTPUT_FILE, 'w', newline="") as f:
        f.write(json.dumps(zonas_json))



if __name__ == '__main__':
    get_bus_lines()
