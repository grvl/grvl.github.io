"""set_districts_on_parkgin_places.py

set the district from SP, on the parking place.
"""
import json
import math

from sp_districts import get_districts, get_district_from_point


_VAGAS_FILE = 'data/vagas/ZonaAzuVagas_DF_ID_latlong.json'
_OUTPUT_FILE_RAW = 'data/vagas/vagas_latlong.csv'
_OUTPUT_FILE_SCORED = 'data/vagas/vaga_district_scored.csv'


def get_vagas(districts=None):
    """Returns a list of dicts with info about each reserved parking area.
    """
    with open(_VAGAS_FILE,  "r") as f:
        vagas_json = json.load(f)

    districts = districts or get_districts()

    vagas = []
    for vaga in vagas_json['features']:
        lat = vaga['geometry']['coordinates'][1]
        lng = vaga['geometry']['coordinates'][0]
        dtc = get_district_from_point(
            districts,
            latitude=lat,
            longitude=lng)
        code, name, area = ('0', 'none', 0) if dtc is None else (
            dtc['code'],
            dtc['name'],
            dtc['polygon'].area * 100000    # Area is in an arbitrary unit.
        )

        vagas.append({
            'district_id': code,
            'district_name': name,
            'district_area': str(area),
            'place': vaga['properties']['Local'],
            'qty': str(vaga['properties']['Quantidade']),
            'area': vaga['properties']['Area'],
            'type': vaga['properties']['Tipo'],
            'lat': str(lat),
            'long': str(lng),
        })
    return vagas


def _export(headers, lines, outfile):
    # Writes to file.
    lines = sorted(lines, key=lambda el: int(el[0]))
    with open(outfile, 'w') as f:
        f.write('\n'.join(','.join(map(lambda el: el.encode('utf-8'), line))
                          for line in ([headers] + lines)))


def export_raw(vagas=None):
    """Exports to csv file the raw data about parking spaces.

    Each line corresponds to a reserved parking area.
    """
    vagas = vagas or get_vagas()
    print('Exporting raw data...')

    # Builds data.
    headers = ['district_id', 'district_name', 'qty', 'area', 'lat', 'long']
    lines = [
        [vaga[attr] for attr in headers]
        for vaga in vagas
    ]

    _export(headers, lines, _OUTPUT_FILE_RAW)


def export_scored(districts=None, vagas=None):
    """Exports to csv file scores for each district based parking spaces info.
    """
    districts = districts or get_districts()
    vagas = vagas or get_vagas()

    # Calculates each districts score.
    scores = {
        dtc['code']: math.log(1 + sum(
            map(
                lambda vaga: int(vaga['qty']),
                filter(lambda vaga: vaga['district_id'] == dtc['code'], vagas)
            )
        ) / dtc['polygon'].area)
        for dtc in districts
    }

    max_score = max(scores.values())     # Normalization factor.

    headers = ['district_id', 'district_name', 'score']
    lines = [
        [
            dtc['code'],
            dtc['name'],
            str(scores[dtc['code']] / max_score),
        ]
        for dtc in districts
    ]

    print('Exporting district scores...')
    _export(headers, lines, _OUTPUT_FILE_SCORED)


if __name__ == '__main__':
    districts = get_districts()
    vagas = get_vagas(districts)
    export_raw(vagas)
    export_scored(districts, vagas)
    print('Done.')
