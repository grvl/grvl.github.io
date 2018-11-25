#!python

'''bus_line_crawler.py

Read bus lines registered in bus_lines.json and calculates an accessibility
rate for each line based on the information at http://olhovivo.sptrans.com.br
The rate is a percentual calculated as the total departures per number of
departures with accessibility.
'''

import json
import csv
import urllib.request
from bs4 import BeautifulSoup
import json
import re

print("Reading JSON")
data = json.load(open('data/bus_lines.json'))
print("Json loaded")

lines_names = []
directions_names = []
missing_lines = ['METRÔ', 'CPTM']
success_lines = []
error_lines = []
not_found_lines = []
shapes = []

for line in data:
    line_name = line['route_id']
    direction = line['direction']
    shape = line['shape']
    if all(str not in line_name for str in missing_lines):
        lines_names.append(line_name)
        directions_names.append(direction)
        shapes.append(shape)


url_start = "http://itinerarios.extapps.sptrans.com.br/PlanOperWeb/detalheLinha.asp?TpDiaID=0&project=OV&lincod="
url_end = "&dfsenid="

with open('data/accessibility.json','w', newline="") as out:

    for idx, line_name in enumerate(lines_names):
        print("Crawling line %s, direction %s" % (line_name, directions_names[idx]))
        url = (url_start + line_name + url_end + directions_names[idx])
        try:
            page = urllib.request.urlopen(url)
            soup = BeautifulSoup(page, "html.parser")
            table = soup.find("table", {"class":"tabelaHorarios"})

            if table is not None:
                departures_total = 0
                accessibles_total = 0
                for row in table.findAll("tr")[1:]:
                    col = row.findAll("td")

                    departure_number = int(col[1].text)
                    departures_total += departure_number

                    accessibles = len(re.findall(r'(?=horarioAdaptado)', str(col[2])))
                    accessibles_total += accessibles

                percentual = accessibles_total/departures_total
                line_info = {"route_id": line_name, "departures": departures_total, "departures_adapted": accessibles_total, "direction": directions_names[idx], "accessibility_score": percentual, "shape": shapes[idx]}
                success_lines.append(line_info)
            else:
                print("Page not found for line %s, direction %s" % (line_name, directions_names[idx]))
                line_info = (line_name, directions_names[idx])
                not_found_lines.append(line_info)
        except:
            print("Error processing line %s, direction %s" % (line_name, directions_names[idx]))
            line_info = (line_name, directions_names[idx])
            error_lines.append(line_info)

    out.write(json.dumps(success_lines))

print("############################")
print("Total successful lines %s" % len(success_lines))
print("Total lines with error %s" % len(error_lines))
print("Total lines not found %s" % len(not_found_lines))
print("############################")
