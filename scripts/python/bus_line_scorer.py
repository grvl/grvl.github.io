"""bus_line_scorer.py

Scores each district based on bus lines.
"""

import json

from math import log

from sp_districts import get_districts, is_line_in_district


_INPUT_FILE = 'data/bus_lines_accessibility.json'
_OUTPUT_FILE = 'data/bus_lines_scores.csv'


def get_bus_lines():
    """Returns an object with raw bus lines data.
    """
    with open(_INPUT_FILE,  'r') as f:
        bus_lines_json = json.load(f)

    for bus_line in bus_lines_json:
        # Transforms coordinates to GeoJson standard.
        bus_line['shape'] = map(lambda pair: (pair['lng'], pair['lat']),
                                bus_line['shape'])

    return bus_lines_json


def calculate_score(districts=None, bus_lines=None):
    """Scores each district, based on bus lines data.
    """
    bus_lines = bus_lines or get_bus_lines()
    districts = districts or get_districts()

    for district in districts:
        print('Calculating score for {}...'.format(district['name']))
        district['weight'] = 0
        district['count'] = 0
        for bus_line in bus_lines:
            if is_line_in_district(district, bus_line['shape']):
                district['weight'] += bus_line['accessibility_score']
                district['count'] += 1

        # Districts score is the "density" of weighted bus lines.
        district['score'] = log(district['weight'] / district['polygon'].area)

    # Normalizes scores.
    max_score = max(district['score'] for district in districts)
    for district in districts:
        district['score'] = district['score'] / max_score

    return districts


def export_csv(districts):
    """Exports result to a csv file.
    """
    headers = ['district_id', 'name', 'count', 'weight', 'score']
    lines = [
        [
            dtc['code'],
            dtc['name'],
            str(dtc['count']),
            str(dtc['weight']),
            str(dtc['score']),
         ]
        for dtc in districts
    ]

    lines = sorted(lines, key=lambda line: int(line[0]))

    # Writes to file.
    with open(_OUTPUT_FILE, 'w') as f:
        f.write('\n'.join(','.join(line) for line in ([headers] + lines)))



if __name__ == '__main__':
    export_csv(calculate_score())
