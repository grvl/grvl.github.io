
PROP_FIELD_REGION_NAME = "name";
HTML_TAG_REGION_NAME = "region-box";

//TODO Insert ALL RANKS
PROP_FIELD_SCORE_GENERAL = "fnl_scr";
PROP_FIELD_RANK_GENERAL = "fnl_scr";
HTML_TAG_SCORE_GENERAL = "score-final";
HTML_TAG_RANK_GENERAL = "ranking-final";

const AXES = [
    'total',
    'venues',
    'topography',
    'parking',
    'bus',
    'subway',
]

AXES_DESCRIPTION = {
    'total': 'Geral',
    'venues': 'Estabelecimentos',
    'topography': 'Topografia',
    'parking': 'Vagas',
    'bus': 'Ônibus',
    'subway': 'Metrô'
}

AXES_AVERAGE = {
    'total': 0,
    'venues': 0,
    'topography': 0,
    'parking': 0,
    'bus': 0,
    'subway': 0,
}

AXES_COUNT = {
    'total': 0,
    'venues': 0,
    'topography': 0,
    'parking': 0,
    'bus': 0,
    'subway': 0,
}

var DISTRICTS_JSON;
var ZONAS_JSON;

var general_score_layer = L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'});

var current_baselayer = 'Geral';
var current_region = {};
var baseMaps = {};
var overlayMaps = {};

var mymap = L.map('mapid', {
  center: [-23.558977, -46.731444],
  zoom: 11,
});

mymap.on('baselayerchange', function(e) { current_baselayer = e.name });

function get_average_values(features) {
  AXES.forEach((axe) => {
    AXES_AVERAGE[axe] = 0;
  });

  AXES.forEach((axe) => {
    features.forEach((feature) => {
      value = feature.properties.scores[axe].value;
      if(value != null) {AXES_COUNT[axe] += 1};

      AXES_AVERAGE[axe] +=  feature.properties.scores[axe].value
    });

    AXES_AVERAGE[axe] /= AXES_COUNT[axe];
  })
}

function style_for_axe(axe) {
    return function(region) {
      return {
          fillColor: region.properties.scores[axe].color,
          weight: 2,
          opacity: 0.7,
          color: 'white',
          dashArray: '3',
          fillOpacity: 0.7
      };
    };
}

var xablau;
function regions_border(region) {
    xablau = region;
    return {
        fillColor: region.properties.COR,
        weight: 3,
        opacity: 1,
        color: '#151515',
        fillOpacity: 0
    };
}

function highlightFeature(e) {
  if(current_region[current_baselayer] != null) {
    resetHighlight(current_region[current_baselayer]);
  }

  var layer = e.target;

  layer.setStyle({
    weight: 3,
    color: '#4F70CE',
    dashArray: '',
    fillOpacity: 0.7,
    opacity: 1,
  });

  if (!L.Browser.ie && !L.Browser.opera && !L.Browser.edge) {
    layer.bringToFront();
  }
}

function resetHighlight(e) {
  if(e != null) {
    if(current_region[current_baselayer] == null || e.target.feature.properties.id != current_region[current_baselayer].target.feature.properties.id) {
      var layer = e.target;
      var default_style = e.target.defaultOptions.style(layer.feature);
      layer.bringToBack();

      layer.setStyle(default_style);
      layer.addTo(mymap);
    }
  }
}

function truncate_score(score) {
  return score == null ? '-' : (score + '.00').substr(0,4);
}

function changeTargetForSpiderGraph(region) {
  scores = region.scores;

  AXES.forEach((axe) => {
    score = document.getElementsByClassName('score-' + axe)[0];
    ranking = document.getElementsByClassName('ranking-' + axe)[0];

    score.innerHTML = truncate_score(scores[axe].value)
    ranking.innerHTML = scores[axe].ranking + "&#186";
  });


  region_name = document.getElementsByClassName(HTML_TAG_REGION_NAME)[0];
  region_name.innerHTML = region[PROP_FIELD_REGION_NAME];

  region_name.onchange(region);
}

function zoomToFeature(e) {
  changeTargetForSpiderGraph(e.target.feature.properties);
  old_region = current_region[current_baselayer];
  current_region[current_baselayer] = e;
  resetHighlight(old_region);
}

// Apply this events on each feature layer of the map
function onEachFeature(feature, layer) {
  layer.on({
    mouseover: highlightFeature,
    mouseout: resetHighlight,
    click: zoomToFeature
  })
}

var START_REGION_ID = 78;

function plot_data(axe, data) {
  var layer_group = L.layerGroup();
  layer_group.addLayer(general_score_layer);
  styling = style_for_axe(axe);

  data.forEach((e) => {
    if(e.properties.id == START_REGION_ID) {
      changeTargetForSpiderGraph(e.properties);
    }

    geojson = L.geoJson(e, {
      style: styling,
      onEachFeature: onEachFeature
    }).bindTooltip((layer) => {
      name = layer.feature.properties.name
      zone = layer.feature.properties.zone
      return name + '<br>' + 'Região: ' + zone;
    })
    layer_group.addLayer(geojson);
  })

  baseMaps[AXES_DESCRIPTION[axe]] = layer_group;
}

function fetch_json_file(filename) {
  console.log(filename);
  return fetch(filename).then((response) => { return response.json() });
}


function fetch_data(filename) {
  return new Promise((resolve, reject) => {
    fetch_json_file(filename).then((json_data) => {
      resolve(json_data);
    })
  })
}

function plot_base_layers(data) {
  AXES.forEach((axe) => {
    plot_data(axe, data);
  });
}

function plot_overlay_points(description, data, icon) {
  var layer_group = L.featureGroup();
  data.forEach((e) => {
    geojson = L.geoJson(e, {
      pointToLayer: function(poing, latlng) {
        return L.marker(latlng, {bubblingMouseEvents: true, icon: icon});
      }
    })
    layer_group.addLayer(geojson);
  })
  overlayMaps[description] = layer_group;
}

function build_icon(size, url) {
  return L.icon({
    iconUrl: url,
    iconSize: size,
    popupAnchor: [-3, -76],
  });
}

function build_map() {
    Promise.all([
      fetch_data('js/data/distritos-ranked.json')
      .then((data) => {
        DISTRICTS_JSON = data.features;
        get_average_values(data.features);
        plot_base_layers(data.features);
      }),

    //  fetch_data('js/data/vagas_zona_azul.json')
    //  .then((data) => {
    //    var venues_icon = build_icon([10,10], 'img/icons/metro.jpg')
    //    plot_overlay_points('Estabelecimentos', data.features, venues_icon);
    //  }),

      fetch_data('js/data/metro.json')
      .then((data) => {
        var metro_icon = build_icon([10,10], 'img/icons/metro.jpg')
        plot_overlay_points('Metrô', data.features, metro_icon);
      }),

      fetch_data('js/data/cptm.json')
      .then((data) => {
        var cptm_icon = build_icon([10,10], 'img/icons/cptm.png')
        plot_overlay_points('CPTM', data.features, cptm_icon);
      }),

      fetch_data('js/data/vagas_zona_azul.json')
      .then((data) => {
        var vagas_icon = build_icon([25,25], 'img/icons/vaga-deficiente.png')
        plot_overlay_points('Vagas', data.features, vagas_icon);
      }),

      fetch_data('js/data/sp_zonas.json')
      .then((data) => {
        ZONAS_JSON = data.features;
      })


    ]).then((values) => {

      Object.keys(baseMaps).forEach(key => {
        ZONAS_JSON.forEach((zone) => {
          L.geoJson(zone, {
            interactive: false,
            style: regions_border
          }).addTo(baseMaps[key])
        })
      })

      L.control.layers(baseMaps, overlayMaps).addTo(mymap);
      baseMaps['Geral'].addTo(mymap);

      buildHtmlTable();
    });
}

function buildHtmlTable() {
  var table = $('#ranking-table');

  var sorted = DISTRICTS_JSON.sort(function(a, b) {return (b.properties["scores"]["total"].value > a.properties["scores"]["total"].value) ? 1 : ((b.properties["scores"]["total"].value < a.properties["scores"]["total"].value) ? -1 : 0)})
  for (var i = 0; i < sorted.length; i++) {
    var row$ = $('<tr/>');
    row$.append($('<td/>').html(i + 1));
    row$.append($('<td/>').html(sorted[i]["properties"]["name"]));
    AXES.forEach((axe) => {
      var cellValue = truncate_score(sorted[i]["properties"]["scores"][axe].value);
      if (cellValue == null) cellValue = "";
      row$.append($('<td/>').html(cellValue));
    })
    table.append(row$);
  }

  sorttable.makeSortable(table[0]);
}

build_map();
