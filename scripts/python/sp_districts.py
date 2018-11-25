"""sp_districts.py

Defines methods to load Districts and get the District that
contains a given lat/long pair.
"""
import json

from shapely.geometry import Point, LineString
from shapely.geometry.polygon import Polygon


_DISTRICTS_FILENAME = 'data/distritos-latlong.json'


def get_district_from_point(districts, latitude, longitude):
    """Returns the District that contains a lat/long pair.
    """
    if latitude < -25.0 or longitude > -45:
        raise ValueError('Invalid coords for SP. Maybe the order is inverted?')
    point = Point(longitude, latitude)  # GeoJsons invert the pair order.
    for district in districts:
        if district['polygon'].contains(point):
            return district


def get_districts():
    """Returns a list of dicts containing District info and its Polygon.
    """
    def get_district_obj(district):
        # Builds a dict with info about each district and builds a Polygon obj.
        return {
            'polygon': Polygon(district['geometry']['coordinates'][0]),
            'name': district['properties']['ds_nome'],
            'code': district['properties']['ds_codigo'],
        }

    with open(_DISTRICTS_FILENAME, 'r') as f:
        districts_json = json.load(f)
    return map(get_district_obj, districts_json['features'])


def is_line_in_district(district, line_coordinates):
    """Returns True if line intersects district, false otherwise.

    Parameters: district obj, list of latitudes and list of longitudes.
    """
    return district['polygon'].intersects(LineString(line_coordinates))
