"""set_districts_on_parkgin_places.py

set the district from SP, on the parking place.
"""
import json


_VAGAS_FILE = 'data/vagas/ZonaAzuVagas_DF_ID_latlong.json'

with open(_VAGAS_FILE,  "r") as f:
    delete = []
    vagas_json = json.load(f)
    for i in range(0, len(vagas_json['features'])):
        if vagas_json['features'][i]['properties']['Tipo'] != 'ID' and vagas_json['features'][i]['properties']['Tipo'] != 'DF':
            print(vagas_json['features'][i]['properties']['Tipo'])
            delete.append(i)
        else:
            print(i)

for num in reversed(delete):
    del vagas_json['features'][num]

with open(_VAGAS_FILE,'w', newline="") as out:
    out.write(json.dumps(vagas_json))
