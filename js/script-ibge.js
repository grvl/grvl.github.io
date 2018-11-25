r = document.getElementsByClassName("region-box")[0];


Highcharts.theme = {
   colors: ['#FE9A2E', '#50B432', '#ED561B', '#DDDF00', '#24CBE5', '#64E572',
      '#FF9655', '#FFF263', '#6AF9C4'],
   // chart: {
   //    backgroundColor: {
   //       linearGradient: { x1: 0, y1: 0, x2: 1, y2: 1 },
   //       stops: [
   //          [0, '#F3F3F3'],
   //          [1, '#F3F3F3']
   //       ]
   //    },
   //    borderWidth: 0,
   //    plotBackgroundColor: '#F3F3F3',
   //    plotShadow: false,
   //    plotBorderWidth: 0
   // },
   title: {
      style: {
         color: '#000',
         font: 'bold 2.3em "Trebuchet MS", Verdana, sans-serif',
         align: 'center'
      }
   },
   subtitle: {
      style: {
         color: '#666666',
         font: 'bold 12px "Trebuchet MS", Verdana, sans-serif'
      }
   },
   xAxis: {
      gridLineWidth: 1,
      lineColor: '#000',
      tickColor: '#000',
      labels: {
         style: {
            color: '#000',
            font: '11px Trebuchet MS, Verdana, sans-serif'
         }
      },
      title: {
         style: {
            color: 'purple',
            fontWeight: 'bold',
            fontSize: '12px',
            fontFamily: 'Trebuchet MS, Verdana, sans-serif'

         }
      }
   },
   yAxis: {
      minorTickInterval: 'auto',
      lineColor: '#000',
      lineWidth: 1,
      tickWidth: 1,
      tickColor: '#000',
      labels: {
         style: {
            color: '#000',
            font: '11px Trebuchet MS, Verdana, sans-serif'
         }
      },
      title: {
         style: {
            color: '#333',
            fontWeight: 'bold',
            fontSize: '12px',
            fontFamily: 'Trebuchet MS, Verdana, sans-serif'
         }
      }
   },
   legend: {
      itemStyle: {
         font: '9pt Trebuchet MS, Verdana, sans-serif',
         color: 'black'

      },
      itemHoverStyle: {
         color: '#039'
      },
      itemHiddenStyle: {
         color: 'gray'
      }
   },
   labels: {
      style: {
         color: '#99b'
      }
   },

};

// Apply the theme
function remove_hidden_class() {
  var FADEIN_CLASS = "fade-in";
  elements = document.getElementsByClassName("radar-statistics");

  Array.from(elements).forEach((elem) => {
    elem.classList.add(FADEIN_CLASS);
  });
};

r.onchange = function(region_data) {
  Highcharts.setOptions(Highcharts.theme);
  remove_hidden_class();
  scores = region_data.scores

  // var radar_chart = Highcharts.chart('chart', {
  //
  //     chart: {
  //         polar: true,
  //         type: 'line',
  //         showAxes: false,
  //         alignTicks: true
  //     },
  //
  //     title: {
  //         text: '',
  //         floating: true
  //     },
  //
  //     pane: {
  //         size: '80%'
  //     },
  //
  //     xAxis: {
  //         categories: ['Estabelecimentos', 'Topografia', 'Metrô', 'Ônibus', 'Vagas'],
  //         tickmarkPlacement: 'on',
  //         lineWidth: 0,
  //     },
  //
  //     yAxis: {
  //         gridLineInterpolation: 'polygon',
  //         lineWidth: 0,
  //         max: 12,
  //         min: -2.0,
  //         endOnTick: false,
  //         startOnTick: false,
  //         categories: [],
  //         labels: {
  //           step: 3
  //         }
  //     },
  //
  //     tooltip: {
  //         shared: true,
  //         pointFormat: '<span style="color:{series.color}">{series.name}: <b>{point.y:,.0f}</b><br/>'
  //     },
  //
  //     navigation: {
  //       buttonOptions: {
  //         enabled: false
  //       }
  //     },
  //
  //     series: [{
  //         name: 'Média',
  //         data: [AXES_AVERAGE.venues, AXES_AVERAGE.topography, AXES_AVERAGE.subway,
  //                AXES_AVERAGE.bus, AXES_AVERAGE.parking],
  //         pointPlacement: 'on'
  //     }, {
  //         name: region_data.name,
  //         data: [scores.venues.value, scores.topography.value, scores.subway.value,
  //                scores.bus.value, scores.parking.value],
  //         pointPlacement: 'on'
  //     }]
  //
  // });
}
