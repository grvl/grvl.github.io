"""Script for converting from UTM coordinates to lat/long.
"""

from pyproj import Proj, transform

import json
import numpy

# define projections
wgs84 = Proj(init='epsg:4326')
brazilian_grid = Proj(init='epsg:31983')

# IN_FILENAME = '/home/joao/Downloads/SIRGAS_SHP_distrito_polygon.json'
IN_FILENAME = '/home/joao/Downloads/SIRGAS_SHP_acessibilidadesmped_point.json'
OUT_FILENAME = 'out.json'


# load in data
with open(IN_FILENAME, 'r') as f:
    data = json.load(f)


def process_point(coord_pair):
    print coord_pair
    x1 = coord_pair[0]
    y1 = coord_pair[1]
    lat_grid, lon_grid = numpy.meshgrid(x1, y1)
    # do transformation
    coord_pair = transform(brazilian_grid, wgs84, lat_grid, lon_grid)
    coord_pair = [coord_pair[0][0][0], coord_pair[1][0][0]]
    return coord_pair


def process_polygon(coords):
    res = []
    for index1 in range(len(coords)):
        for index2 in range(len(coords[index1])):
            coords[index1][index2] = process_point(coords[index1][index2])
    return coords


# traverse data in json string
for feature in data['features']:
    # print feature['geometry']['type']
    # print feature['geometry']['coordinates']

    # all coordinates
    coords = feature['geometry']['coordinates']

    try:
        coords = process_polygon(coords)
    except TypeError:
        # GeoJson element is a point, not a polygon
        coords = process_point(coords)

    feature['geometry']['coordinates'] = coords

# write reprojected json to new file
with open(OUT_FILENAME, 'w') as f:
    f.write(json.dumps(data))
