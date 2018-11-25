"""global_scorer.py

Fetches data from all .csv files and consolidates the final global score
for each district in a GeoJSON file.
"""

import json

# Hack to force float precision in output file.
from json import encoder
_PRECISION = 4  # Floating point precision.
encoder.FLOAT_REPR = lambda o: format(o, '.{}f'.format(_PRECISION))


_DISTRICTS_FILE = 'data/distritos-simple-latlong.json'
_OUTPUT_FILE = '../../js/data/distritos-ranked.json'


# Dict containing input data. It is of the following format:
# {score_name: (filename, district_id_field_name)}
_SCORES_INPUTS = {
    'venues': ('data/estabelecimentos/venues-score.csv', 'district_id', 'score'),
    'topography': ('../r/final-score.csv', 'ds_codigo', 'topography'),
    'parking': ('../r/final-score.csv', 'ds_codigo', 'parking'),
    'bus': ('../r/final-score.csv', 'ds_codigo', 'bus'),
    'subway': ('../r/final-score.csv', 'ds_codigo', 'railway'),
}

# Types of possible fields in CSV files. Missing fields are treated as strings.
_FIELD_TYPES = {
    'district_id': int,
    'ds_codigo': int,
    'score': float,
    'final_score': float,
    'topography': float,
    'parking': float,
    'bus': float,
    'railway': float,
}

# Weights for calculating final global average.
_WEIGTHS = {
    'venues': 1.0,
    'topography': 1.0,
    'parking': 1.0/3.0,
    'bus': 1.0/3.0,
    'subway': 1.0/3.0,
}


_MIN_SCORE = 0.0
_MAX_SCORE = 10.0


def get_districts_array():
    """Returns a list of dicts containing District info and its Polygon.
    """
    def get_district_obj(district):
        # Builds a dict with info about each district and builds a Polygon obj.
        return {
            'id': int(district['properties']['ds_codigo']),
            'name': district['properties']['ds_nome'],
            'zone': district['properties']['ds_zona'],
            'scores': {},
        }

    with open(_DISTRICTS_FILE, 'r') as f:
        districts_json = json.load(f)
    return map(get_district_obj, districts_json['features'])


def get_geojson(districts_by_id):
    """Builds the districts GeoJSON from an array with meta-data.
    """
    with open(_DISTRICTS_FILE, 'r') as f:
        geojson = json.load(f)

    # Sorts both arrays ensure we don't mix data from different districts.
    geojson['features'] = sorted(
        geojson['features'],
        key=lambda dtc: int(dtc['properties']['ds_codigo'])
    )
    districts_data = sorted(
        districts_by_id.values(),
        key=lambda dtc: dtc['id']
    )

    # Stores data from districts_by_id in GeoJSON's district array.
    for idx in range(len(districts_data)):
        geojson['features'][idx]['properties'] = districts_data[idx]

    return geojson


def _from_csv_to_dicts(filename):
    """Converts a CSV file to a list of dicts.
    """
    def get_value(field_name, value):
        try:
            return _FIELD_TYPES.get(field_name, str)(value)
        except ValueError:
            return None

    with open(filename, 'r') as f:
        lines = f.readlines()

    result = []
    headers = lines[0].replace('"', '').replace('\n', '').split(',')
    for line in lines[1:]:
        values = line.replace('"', '').replace('\n', '').split(',')
        result.append({
            headers[idx]: get_value(headers[idx], values[idx])
            for idx in range(len(values))
        })
    return result


def int_lin(y1, y2, x1, x2, score):
    """Interpolates score in a linear function.
    """
    return y1 + (score - x1) * (y2 - y1) / (x2 - x1)


def _interpolate_color(score):
    """Returns a HEX color code representing the score (ranged from 0 to 1).
    """
    RED = (206, 63, 62)
    GREEN = (38, 165, 112)
    YELLOW = (253, 211, 95)

    YELLOW_THRESHOLD = 0.5 * _MAX_SCORE

    if score is None:
        return '#636466'    # Gray.
    elif score < YELLOW_THRESHOLD:
        color1, color2 = RED, YELLOW
        low, high = _MIN_SCORE, YELLOW_THRESHOLD
    else:
        color1, color2 = YELLOW, GREEN
        low, high = YELLOW_THRESHOLD, _MAX_SCORE

    rgb = [int(int_lin(c1, c2, low, high, score)) for c1, c2 in zip(color1, color2)]
    return '#{:02X}{:02X}{:02X}'.format(*rgb)


def get_partial_score(districts_by_id, score_name):
    """Injects the calculated score of "score_name" into districts_by_id dict.
    """
    # Gets the scores data from appropriate CSV file.
    filename, id_field, score_field = _SCORES_INPUTS[score_name]
    return _save_scores(
        districts_by_id,
        _from_csv_to_dicts(filename),
        score_name,
        id_field,
        score_field,
    )


def get_global_score(districts_by_id):
    """Injects the calculated global score into districts_by_id dict.

    Must be called after all partial scores have been calculated.
    """
    def global_score(dtc):
        # Returns the weighted avg, or None if any partial score is None.
        partials = [
            None if dtc['scores'][score_name]['value'] is None else
            dtc['scores'][score_name]['value'] * _WEIGTHS[score_name]
            for score_name in _SCORES_INPUTS.keys()
        ]
        return (None if None in partials else
                sum(partials) / sum(_WEIGTHS.values()))

    scored_districts = []
    for dtc in districts_by_id.values():
        scored_districts.append({
            'id': dtc['id'],
            'name': dtc['name'],
            'score': global_score(dtc),
        })
    return _save_scores(
        districts_by_id,
        scored_districts,
        score_name='total',
        id_field='id',
        score_field='score',
        normalize=False,
    )


def _save_scores(districts_by_id,
                 scored_districts,
                 score_name,
                 id_field,
                 score_field,
                 normalize=True):
    """Saves scores into objects of a districts dict.
    """
    def intscore(val):
        return int(val * 10 ** _PRECISION) if val is not None else None

    # Normalizes scores.
    nrm_scores = []
    scores = [dtc[score_field] for dtc in scored_districts]
    min_s = min(filter(lambda val: val is not None, scores))
    max_s = max(scores)
    for dtc in scored_districts:
        scr = dtc[score_field]
        if scr is None:
            dtc['score'] = None
        elif normalize:
            dtc['score'] = int_lin(_MIN_SCORE, _MAX_SCORE, min_s, max_s, scr)
        else:
            dtc['score'] = scr
        nrm_scores.append(intscore(dtc['score']))
    nrm_scores = sorted(nrm_scores, reverse=True)

    # Stores result in districts array.
    for dtc in scored_districts:
        districts_by_id[dtc[id_field]]['scores'][score_name] = {
            'value': dtc['score'],
            'color': _interpolate_color(dtc['score']),
            'ranking': nrm_scores.index(intscore(dtc['score'])) + 1,
        }

    return districts_by_id


if __name__ == '__main__':
    districts_by_id = {dtc['id']: dtc for dtc in get_districts_array()}

    for score_name in _SCORES_INPUTS.keys():
        print('Calculating scores for {}...'.format(score_name))
        districts_by_id = get_partial_score(districts_by_id, score_name)

    print('Calculating global scores...')
    districts_by_id = get_global_score(districts_by_id)

    geojson = get_geojson(districts_by_id)

    print('Exporting...')
    with open(_OUTPUT_FILE, 'w') as f:
        json.dump(geojson, f)
    print('Done.')
