"""score_venue.py

Calculates scores for each district, based on their venues' individual scores.
"""
import json

from collections import defaultdict

from sp_districts import get_districts, get_district_from_point


# Minimum
MIN_RATING_QTY = 5


_SELO_FILE = 'data/estabelecimentos/prefeitura/selo-prefeitura-latlong.json'
_VENUES_FILE = '/Users/joao/guiaderodas/venue-jsons/venues.json'
_OUTPUT_FILE = 'data/estabelecimentos/venues-score.csv'


def _selo_score(venue):
    """Calculates a venue's score (for venues from "selo" archive).
    """
    # Max score.
    return 5.0


def _gdr_score(venue):
    """Calculates a venue's score (for venues from guiaderodas).
    """
    scores = venue['scores'].values()
    return sum(scores) / len(scores)


def _get_venue_storage(districts):
    """Initializes a dict for storing venues, organized by district.
    """
    # This ensures districts are included even if they have no rated venues.
    res = {district['name']: [] for district in districts}
    res[None] = []   # Hack: avoids exception if venue has no district.
    return res


def _get_gdr_venues(districts, venues_by_district=None):
    """Returns rated venues (from guiaderodas) by district.

    The returned object is a dict of the format:
    {district_name: [scored_venue]}
    """
    with open(_VENUES_FILE, 'r') as f:
        venues_geojson = json.load(f)

    # Initializes the venue storage data structure.
    venues_by_district = venues_by_district or _get_venue_storage(districts)

    # Calculates each venue's score.
    for venue in venues_geojson['features']:

        # Calculates the venue's district.
        try:
            district = get_district_from_point(
                districts,
                latitude=venue['geometry']['coordinates'][1],
                longitude=venue['geometry']['coordinates'][0],
            )
        except ValueError:
            continue
        if district is None:
            continue    # Venue is not in SP city.

        venue = venue['properties']
        venue['district_name'] = district['name']
        venue['district_id'] = district['code']
        venue['score'] =  _gdr_score(venue)

        # Includes venue in district's venue list.
        venues_by_district[venue['district_name']].append(venue)

    return venues_by_district


def _get_selo_venues(districts, venues_by_district=None):
    """Returns rated venues (from "selo") by district.

    The returned object is a dict of the format:
    {district_name: [scored_venue]}
    """
    with open(_SELO_FILE, 'r') as f:
        selo_json = json.load(f)

    # Initializes the venue storage data structure.
    venues_by_district = venues_by_district or _get_venue_storage(districts)

    for selo_venue in selo_json['features']:
        dtc = get_district_from_point(
            districts,
            # GeoJsons invert the pair order.
            latitude=selo_venue['geometry']['coordinates'][1],
            longitude=selo_venue['geometry']['coordinates'][0]
        )

        # Builds venue dict and includes into appropriate list.
        venue = {
            'district_name': dtc['name'] if dtc is not None else None,
            'district_id': dtc['code'] if dtc is not None else None,
            'address': selo_venue['properties']['as_enderec'],
            'selo_id': selo_venue['properties']['as_id'],
            'name': selo_venue['properties']['as_nome'],
            'year': selo_venue['properties']['as_ano'],
            'score': _selo_score(selo_venue),
        }

        # Includes venue in district's venue list.
        venues_by_district[venue['district_name']].append(venue)

    return venues_by_district


def get_venues(districts):
    """
    """
    venues_by_district = _get_gdr_venues(districts)
    venues_by_district = _get_selo_venues(districts, venues_by_district)
    return venues_by_district


def calculate_districts_score(venues_by_district):
    """Calculates thescore of each district.
    """
    result = dict()
    for district_name, venues in venues_by_district.items():
        vscores = map(lambda ven: ven['score'], venues)

        # District's score is 0 if there are too few vscores.
        qty = len(vscores)
        score = (float(sum(vscores)) / qty) if qty >= MIN_RATING_QTY else 'NA'

        result[district_name] = {
            'score': score,
            'total': len(vscores),
            'good': len(filter(lambda scr: scr >= 4.0, vscores)),
            'avg': len(filter(lambda scr: scr < 4.0 and scr > 2.0, vscores)),
            'bad': len(filter(lambda scr: scr <= 2.0, vscores)),
        }

    return result


def export_csv(districts, scores):
    """Exports result to a csv file.
    """
    headers = ['district_id', 'district_name', 'score']     # Column names.

    # Un-does our "hack": removes the "None" key from scores.
    scores.pop(None, None)

    # scores is a dict of score objects, identified by district name.
    lines = []
    for dtc_name, score in scores.items():
        # Gets the corresponding district object.
        district = next(dtc for dtc in districts if dtc['name'] == dtc_name)

        # Appends to output data.
        lines.append([district['code'], district['name'], str(score['score'])])

    lines = sorted(lines, key=lambda line: int(line[0]))

    # Writes to file.
    with open(_OUTPUT_FILE, 'w') as f:
        f.write('\n'.join(','.join(line) for line in ([headers] + lines)))


if __name__ == '__main__':
    print 'Loading districts...'
    districts = get_districts()
    print 'Loading and scoring venues...'
    venues_by_district = get_venues(districts)
    print 'Scoring districts...'
    scores = calculate_districts_score(venues_by_district)
    print 'Exporting...'
    export_csv(districts, scores)
    print 'Done.'


# districts = get_districts()
# venues_by_district = get_venues(districts)
# scores = calculate_districts_score(venues_by_district)
# sorted([(value['total'], key) for key, value in scores.items()])
# sorted([(value['score'], value['total'], key) for key, value in scores.items()])

# for qt in [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50]:

# for qt in [5, 6, 7, 8, 9, 10]:
#     qti = len(filter(lambda el: el[0] >= qt, sorted([(value['total'], key) for key, value in scores.items()])))
#     print qt, qti, 96 - qti
