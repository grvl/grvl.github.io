from flask import Flask, render_template, request
from geopy.geocoders import Nominatim
import psycopg2
import json
import geojson
import numpy as np
import geog
import folium
from shapely.geometry import asShape, mapping, Polygon
from folium import plugins, FeatureGroup, LayerControl
from folium.plugins import MarkerCluster
import branca.colormap as cm

app = Flask(__name__)

@app.route('/coisas',  methods=['GET'])
def endereco():
    return pesquisar_endereco(request.args.get('q'), int(request.args.get('dist')))

@app.route('/pessoas',  methods=['GET'])
def pessoa():
    return pesquisar_pessoa(request.args.get('q'), int(request.args.get('dist')))

#------------------------------------------------------

def get_links (lista, dist):
    new_list = []
    for item in lista:
        aux_dict = {}
        aux_dict['address'] = item.address
        aux_dict['link'] = "/coisas?q="+item.address.replace(",", "%2C").replace(" ", "+")+"&dist="+str(dist)
        new_list.append(aux_dict)
    return new_list

def pesquisar_endereco(endereco, distancia = 1):
    # Pesquisa por endereco é feita pelo banco
    dbname = 'pesquisa'
    user = 'lima'
    pswd = '123456'

    if distancia > 5:
        distancia = 5;

    geolocator = Nominatim(user_agent="usp_TCC", timeout = 5)
    try:
        locations = geolocator.geocode(endereco, exactly_one = False)
        if locations is None:
            return "Endereço não encontrado."

    except Exception as e:
        print(e)
        return "Nao foi possivel completar a pesquisa. Erro na pesquisa de endereço."

    valid_locations = []
    for loc in locations:
        if 'SP, Microrregião de São Paulo' in loc.address:
            # print(loc.address + ' ' + str(loc.latitude) + ' ' + str(loc.longitude))
            valid_locations.append(loc)

    location = valid_locations.pop(0)

    p = asShape({'type': 'Point','coordinates': [location.longitude,location.latitude]})  # GeoJsons inverts the pair order.


    # Cria um círculo para enviar para o PostGIS
    n_points = 20
    d = distancia * 1000  # meters
    angles = np.linspace(0, 360, n_points)
    polygon = geog.propagate(p, angles, d)
    area = geojson.Feature(geometry = mapping(Polygon(polygon)))

    zona = {"type": "FeatureCollection", "features": []}

    try:
        # conn = psycopg2.connect("dbname='"+dbname+"' user='"+user+"' host='eclipse.ime.usp.br' password='"+pswd+"'")
        conn = psycopg2.connect("dbname='"+dbname+"' user='"+user+"' host='127.0.0.1' password='"+pswd+"'")
    except Exception as e:
        print(e)
        return "Nao foi possivel completar a pesquisa. Erro na conexão com o banco."

    # [nome_do_banco, display_name_do_dado]
    for banco in [['bus_line', "route_id, accessibility_score"], ['cptm', "concat(etr_nome, ' - LINHA ', etr_linha) as name"], ['metro2', "concat(emt_nome, ' - LINHA ', emt_linha) as name"], ['prefeitura_venues', 'as_nome'], ['venues', "name, scores"], ['zona_azul', "local, tipo"]]:
        try:
            cur = conn.cursor()
            # Comando PostGIS para pesquisar por distância
            cur.execute("select ST_AsGeoJSON(wkb_geometry), "+ banco[1]+" from "+banco[0]+" where  ST_Crosses(ST_GeomFromGeoJSON('"+str(area['geometry'])+"'), ST_GeomFromGeoJSON(ST_AsGeoJSON(wkb_geometry))) OR ST_Contains(ST_GeomFromGeoJSON('"+str(area['geometry'])+"'), ST_GeomFromGeoJSON(ST_AsGeoJSON(wkb_geometry)));")
            rows = cur.fetchall()
        except Exception as e:
            print(e)
            return "Nao foi possivel completar a pesquisa. Erro na pesquisa do banco."

        for row in rows:
            properties ={"type": banco[0], "name": row[1].replace("'", "\\'"), "other":""}
            if len(row) > 2:
                properties['other'] = str(row[2]).replace("'", "\\'")
            zona['features'].append({"geometry": json.loads(row[0]), "type": "Feature", "properties": properties})

    conn.close()

    m = folium.Map([location.latitude,location.longitude], tiles='cartodbpositron', zoom_start=13 - distancia/5)

    # Cria um círculo para visualização. Não usa o mesmo criado lá em cima simplesmente por que folium.Circle tinha funcionalidades melhores
    circle_group = FeatureGroup(name='Círculo')
    folium.Circle(
        location=[location.latitude, location.longitude],
        radius=d,
        color='black',
        weight=1,
        fill_opacity=0.3,
        opacity=1,
        fill_color='red',
        fill=False,  # gets overridden by fill_color
        tooltip=location.address,
    ).add_to(circle_group)

    circle_group.add_to(m)

    # Funções para retornar o que exibir para cada tipo.
    def return_icon(item):
        icon_type = item['properties']['type']

        if icon_type == 'bus_line':
            return folium.Icon(color= 'black', icon='bus', prefix = 'fa')
        elif icon_type == 'cptm':
            return folium.Icon(color = 'red', icon='train', prefix = 'fa')
        elif icon_type == 'prefeitura_venues':
            return folium.Icon(color = 'green', icon='universal-access', prefix = 'fa')
        elif icon_type == 'venues':
            nota = float(item['properties']['other'][10:13])
            cor = 'green'
            if nota < 1.7:
                cor = 'red'
            elif nota < 3.4:
                cor = 'orange'
            return folium.Icon(color = cor, icon='star-half-o', prefix = 'fa')
        elif icon_type == 'zona_azul':
            return folium.Icon(color = 'blue', icon='car', prefix = 'fa')
        elif icon_type == 'metro2':
            return folium.Icon(color = 'darkblue', icon='subway', prefix = 'fa')
    def return_type(db_name):
        if db_name == 'bus_line':
            return "Linha de Ônibus"
        elif db_name == 'cptm':
            return "Estação de CPTM"
        elif db_name == 'prefeitura_venues':
            return "Local com selo de acessibilidade"
        elif db_name == 'venues':
            return "Local com nota no Guia de Rodas"
        elif db_name == 'zona_azul':
            return "Zona azul"
        elif db_name == 'metro2':
            return "Estação de metro"
    def return_other_type(other, info = ""):
        if other == 'bus_line':
            return "Nota: " + str(int(float(info)*100)/100) + "/1"
        elif other == 'venues':
            return "Nota: " + info[10:13]+ "/5"
        elif other == 'zona_azul':
            if info == 'ID':
                return "Tipo: Vaga para idoso"
            elif info == 'DF':
                return 'Tipo: Vaga para pessoa com deficiência'
        return ""


    # Feature groups para poder filtrar no mapa por tipo de dado
    groups = {'bus_line' : FeatureGroup(name = 'Ônibus'),'cptm': FeatureGroup(name = 'CPTM'), 'prefeitura_venues':FeatureGroup(name = 'Selo de acessibilidade'), 'venues':FeatureGroup(name = 'Guia de Rodas'), 'zona_azul':FeatureGroup(name = 'Zona Azul'), 'metro2':FeatureGroup(name = 'Metrô')}

    linear = cm.LinearColormap(['red', 'yellow', 'green'], vmin=0, vmax=1)
    linear.caption = 'Nota da Linha de Ônibus'

    def my_color_function(feature):
        if feature > 0:
            return linear(feature)
        else:
            return '#777777'

    for item in zona['features']:
            # If ponto
            if item['geometry']['type'] == 'Point':
                f = folium.Marker([item['geometry']['coordinates'][1],item['geometry']['coordinates'][0]], icon=return_icon(item))

            # If linha de ônibus
            else:
                line = list([[pair[1], pair[0]] for pair in item['geometry']['coordinates'] ])
                f = folium.PolyLine( line, weight=5, color=my_color_function(float(item['properties']['other'])))

            html = "<b>" + item['properties']['name'] + "</b> <i>("+return_type(item['properties']['type'])+")</i><br>"+return_other_type(item['properties']['type'], item['properties']['other'])+"</br>";
            f.add_child(folium.Popup(html, parse_html=False))
            f.add_to(groups[item['properties']['type']])

    for group in groups:
        groups[group].add_to(m)

    LayerControl().add_to(m)
    return render_template("coisas.html", name = location.address, map = m._repr_html_(), addresses = get_links(valid_locations, distancia))

def pesquisar_pessoa(endereco, distancia = 1):
    arquiv = "js/data/distritos-ranked-ibge.json"
    #arquiv = "/home/interscity/interscity.org/apps/freewheels-teste/js/data/distritos-ranked-ibge.json"

    if distancia > 5:
        distancia = 5;

    f = open(arquiv, 'r')
    mapa = json.load(f)
    f.close()

    geolocator = Nominatim(user_agent="usp_TCC", timeout = 5)
    try:
        locations = geolocator.geocode(endereco, exactly_one = False)
        if locations is None:
            return "Endereço não encontrado."

    except Exception as e:
        print(e)
        return "Nao foi possivel completar a pesquisa. Erro na pesquisa de endereço."

    valid_locations = []
    for loc in locations:
        if 'SP, Microrregião de São Paulo' in loc.address:
            # print(loc.address + ' ' + str(loc.latitude) + ' ' + str(loc.longitude))
            valid_locations.append(loc)
    location = valid_locations.pop(0)


    p = asShape({'type': 'Point','coordinates': [location.longitude,location.latitude]})  # GeoJsons inverts the pair order.

    # Circulo - Escolhi não desenhar ele no mapa por que ele ficava sendo desenhado em cima da divisão de áreas de ponderação, não deixando elas serem clicáveis
    n_points = 20
    d = distancia * 1000  # meters
    angles = np.linspace(0, 360, n_points)
    circle = Polygon(geog.propagate(p, angles, d))
    m = folium.Map([location.latitude,location.longitude], tiles='cartodbpositron', zoom_start=13 - distancia/5)

    linear = cm.LinearColormap(
            ['red', 'yellow', 'green'],
            vmin=0, vmax=1
        )

    def my_color_function(feature):
        if feature > 0:
            return linear(feature)
        else:
            return '#777777'

    soma = {
    'total' : 0,
    'dificuldade_geral' : 0,
    'smped' : 0,
    'enxergar_geral' : 0,
    'ouvir_geral' : 0,
    'caminhar_geral' : 0,
    'intelectual_geral' : 0
    }

    for item in mapa['features']:
        poly = asShape(item['geometry'])

        if not poly.is_valid:
            poly=poly.buffer(0)

        aux = poly.intersection(circle)
        item['properties']['percent'] = 0

        if not aux.is_empty:
            item['properties']['percent'] = aux.area/poly.area
        gj = folium.GeoJson(
            data=item,
            style_function=lambda feature: {
                'fillColor': my_color_function(feature['properties']['percent']),
                'color': '#333333',
                'weight': 1.5,
                'dashArray': '5, 5'
            },
            highlight_function=lambda feature: {
                'color': 'black',
                'weight': 3,
                'dashArray': '5, 5'
            }
        )

        # informações para exibir
        name = item['properties']['name']
        zone = item['properties']['zone']
        total = int(item['properties']['dados_ibge']['total_pessoas'] * item['properties']['percent'])
        soma['total'] += total
        dificuldade_geral = int(total*item['properties']['scores']['dificuldade_geral']['value']/100)
        soma['dificuldade_geral'] += dificuldade_geral
        smped = int(item['properties']['scores']['smped']['value'] * item['properties']['percent'])
        soma['smped'] += smped
        enxergar_geral = int(total*item['properties']['scores']['enxergar_geral']['value']/100)
        soma['enxergar_geral'] += enxergar_geral
        ouvir_geral = int(total*item['properties']['scores']['ouvir_geral']['value']/100)
        soma['ouvir_geral'] += ouvir_geral
        caminhar_geral = int(total*item['properties']['scores']['caminhar_geral']['value']/100)
        soma['caminhar_geral'] += caminhar_geral
        intelectual_geral = int(total*item['properties']['scores']['intelectual_geral']['value']/100)
        soma['intelectual_geral'] += intelectual_geral

        html = '<b>' + name + '</b><br>' + '<b>Região:</b> ' + zone +  '<br><b>Famílias:</b> ' + str(total) +  ' ('+str(int(item['properties']['percent'] * 10000)/100)+'%)<br><b>Famílias com alguém com alguma dificuldade:</b> ' + str(dificuldade_geral) + '<br><b>Famílias com alguém com dificuldade de enxergar:</b> ' + str(enxergar_geral) + '<br><b>Famílias com alguém com dificuldade de ouvir:</b> ' + str(ouvir_geral) + '<br><b>Famílias com alguém com dificuldade de caminhar:</b> ' + str(caminhar_geral) + '<br><b>Famílias com alguém com deficiência intelectual:</b> ' + str(intelectual_geral) + '<br><b>Beneficiários BPC:</b> ' + str(smped)
        gj.add_child(folium.Popup(html))
        gj.add_to(m)

    return render_template("pessoas.html", name = location.address, total = soma['total'], dif = soma['dificuldade_geral'], smped = soma['smped'], enx = soma['enxergar_geral'], ouv = soma['ouvir_geral'], cam = soma['caminhar_geral'], int = soma['intelectual_geral'], map = m._repr_html_(), addresses = get_links(valid_locations, distancia))

# ----------------------------------------------------
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
