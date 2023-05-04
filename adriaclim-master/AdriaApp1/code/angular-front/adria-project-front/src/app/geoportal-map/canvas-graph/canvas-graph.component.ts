import { HttpClient } from '@angular/common/http';
import { Component, EventEmitter, Input, OnChanges, OnInit, Output, SimpleChanges, ViewChild, AfterViewInit} from '@angular/core';
import { EChartsOption, graphic } from 'echarts';
import * as echarts from 'echarts';
import { ElementRef } from '@angular/core';
import { HttpService } from 'src/app/services/http.service';
import * as _ from 'lodash';

@Component({
  selector: 'app-canvas-graph',
  templateUrl: './canvas-graph.component.html',
  styleUrls: ['./canvas-graph.component.scss']
})
export class CanvasGraphComponent implements OnInit, OnChanges, AfterViewInit {
  isLoading!: boolean;
  @Input() idMeta: any;
  @Input() dataset: any;
  @Input() latlng: any;
  // @Input() lat: any;
  // @Input() lng: any;
  // @Input() dateStart: any;
  // @Input() dateEnd: any;
  @Input() variable: any;
  // @Input() dimensions: any;
  @Input() range: any;
  // @Input() latMin: any;
  // @Input() latMax: any;
  // @Input() lngMin: any;
  // @Input() lngMax: any;
  @Input() polygon: any;
  @Input() isIndicator: any;
  @Input() operation: any;
  @Input() statistic: any;
  @Input() context: any;
  @Input() extraParam: any;
  @Input() enableArea: any;
  @Input() circleCoords: any;
  @Output() meanMedianStdev = new EventEmitter<any>();
  @Output() dataTimeExport = new EventEmitter<any>();
  @Output() dataTablePolygon = new EventEmitter<any>();
  @Output() spinnerLoadingChild = new EventEmitter<any>();
  @Output() statisticCalc = new EventEmitter<any>();
  @ViewChild("parent") parentRef!: ElementRef<HTMLElement>;
  myChart: any;
  dateGraphZoom : any[] = [];
  valueGraphZoom : any[] = [];
  // startValue: any;
  // endValue: any =  (document.getElementById('main') as HTMLDivElement).getEchartsInstance().getOption().dataZoom[0]
  months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  chartOption: EChartsOption = {};
  chartOptionBars: EChartsOption = {};
  option: any;
  dataBoxPlot = [900, 345, 393, -108, -154, 135, 178, 286, -119, -361, -203];
  help: any[] = [];
  positive: any[] = [];
  negative: any[] = [];
  dataRes: any;
  startZoom: any;
  endZoom: any;
  data1 = [
    [850, 740, 900, 1200, 930, 850, 950, 980, 980, 880, 1000, 980, 930, 650, 760, 810, 1000, 1000, 960, 960],
    [960, 940, 960, 940, 880, 800, 850, 880, 900, 840, 830, 790, 810, 880, 880, 830, 800, 790, 760, 800],
    [880, 880, 880, 860, 720, 720, 620, 860, 970, 950, 880, 910, 850, 870, 840, 840, 850, 840, 840, 840],
    [890, 810, 810, 820, 800, 770, 760, 740, 750, 760, 910, 920, 890, 860, 880, 720, 840, 850, 850, 780],
    [890, 840, 780, 810, 760, 810, 790, 810, 820, 850, 870, 870, 810, 740, 810, 940, 950, 800, 810, 870]
  ]


  /**********************TEST BOX PLOT */
//   var data1 = [
//     [850, 740, 900, 1070, 930, 850, 950, 980, 980, 880, 1000, 980, 930, 650, 760, 810, 1000, 1000, 960, 960],
//     [960, 940, 960, 940, 880, 800, 850, 880, 900, 840, 830, 790, 810, 880, 880, 830, 800, 790, 760, 800],
//     [880, 880, 880, 860, 720, 720, 620, 860, 970, 950, 880, 910, 850, 870, 840, 840, 850, 840, 840, 840],
//     [890, 810, 810, 820, 800, 770, 760, 740, 750, 760, 910, 920, 890, 860, 880, 720, 840, 850, 850, 780],
//     [890, 840, 780, 810, 760, 810, 790, 810, 820, 850, 870, 870, 810, 740, 810, 940, 950, 800, 810, 870]
// ]

// let p;
// function prova() {
// let p = data1.map((item, index) => {
// return [index, item];
// })
// return p;
// }
// option = {
// // tooltip: {
// //   trigger: 'axis',
// //   axisPointer: {
// //     type: 'cross'
// //   }
// // },
// title: [
// {
// text: 'Michelson-Morley Experiment',
// left: 'center'
// },
// {
// text: 'upper: Q3 + 1.5 * IQR \nlower: Q1 - 1.5 * IQR',
// borderColor: '#999',
// borderWidth: 1,
// textStyle: {
// fontWeight: 'normal',
// fontSize: 14,
// lineHeight: 20
// },
// left: '10%',
// top: '90%'
// }
// ],

// dataset: [
// {
// // prettier-ignore dataset index 0
// source: data1
// },
// {
// //datasetIndex 1
// transform: {
// type: 'boxplot',
// config: { itemNameFormatter: 'expr {value}' },
// }
// },
// //datasetindex 2
// {
// fromDatasetIndex: 1,
// fromTransformResult: 1
// },

// {
// source:  data1.map((item, index) => {
// const average = item.reduce((prev, curr) => prev + curr) / item.length;
// return [index, average];

// }
// )
// }



// ],
// tooltip: {
// trigger: 'item',
// axisPointer: {
// type: 'shadow'
// }
// },
// grid: {
// left: '10%',
// right: '10%',
// bottom: '15%'
// },
// xAxis: {
// type: 'category',
// data: ["expr 0","expr 1","expr 2","expr 3","expr 4"]
// },
// yAxis: {
// type: 'value',
// name: 'km/s minus 299,000',
// },
// series: [
// {
// name: 'Box plot',
// type: 'boxplot',
// datasetIndex: 1,

// tooltip: {
//     formatter: function(param) {
//         return [
//             "Experiment " + param.name + ": ",
//             "upper: " + param.data[5],
//             "Q3: " + param.data[4],
//             "median: " + param.data[3],
//             "Q1: " + param.data[2],
//             "lower: " + param.data[1]
//         ].join("<br/>");
//     }
// },

// },
// {
// name: 'Outlier',
// type: 'scatter',
// datasetIndex: 2,
// },
// {
// name: 'Mean',
// type: 'scatter',
// datasetIndex: 3,
// symbolSize: 10,
// symbol: 'path://M51.911,16.242C51.152,7.888,45.239,1.827,37.839,1.827c-4.93,0-9.444,2.653-11.984,6.905 c-2.517-4.307-6.846-6.906-11.697-6.906c-7.399,0-13.313,6.061-14.071,14.415c-0.06,0.369-0.306,2.311,0.442,5.478 c1.078,4.568,3.568,8.723,7.199,12.013l18.115,16.439l18.426-16.438c3.631-3.291,6.121-7.445,7.199-12.014 C52.216,18.553,51.97,16.611,51.911,16.242z',
// itemStyle: {
// color: 'red',
// },

// tooltip: {
//     formatter: function(param) {
//         return [
//             "Mean " + ": ",
//             param.data[1]
//         ].join("<br/>");
//     }
// },

// }

// ]
// };


optionBoxPlot: any = {
      // tooltip: {
      //   trigger: 'axis',
      //   axisPointer: {
      //     type: 'cross'
      //   }
      // },
      title: [
      {
      text: 'Michelson-Morley Experiment',
      left: 'center'
      },
      {
      text: 'upper: Q3 + 1.5 * IQR \nlower: Q1 - 1.5 * IQR',
      borderColor: '#999',
      borderWidth: 1,
      textStyle: {
      fontWeight: 'normal',
      fontSize: 14,
      lineHeight: 20
      },
      left: '10%',
      top: '90%'
      }
      ],

      dataset: [
      {
      // prettier-ignore dataset index 0
      source: this.data1
      },
      {
      //datasetIndex 1
      transform: {
      type: 'boxplot',
      config: { itemNameFormatter: 'Expr {value}' },
      }
      },
      //datasetindex 2
      {
      fromDatasetIndex: 1,
      fromTransformResult: 1
      },

      {
      source:  this.data1.map((item, index) => {
      const average = item.reduce((prev, curr) => prev + curr) / item.length;
      return [index, average];

      }
      )
      }



      ],
      tooltip: {
      trigger: 'item',
      axisPointer: {
      type: 'shadow'
      }
      },
      grid: {
      left: '10%',
      right: '10%',
      bottom: '15%'
      },
      xAxis: {
      type: 'category',
      data: ["Expr 0","Expr 1","Expr 2","Expr 3","Expr 4"]
      },
      yAxis: {
      type: 'value',
      name: 'km/s minus 299,000',
      },
      series: [
      {
      name: 'Box plot',
      type: 'boxplot',
      datasetIndex: 1,

      tooltip: {
        formatter: function(param:any) {
          const param_smaller = "<span style='display:inline-block;margin-bottom:3px; margin-left:18px; border-radius:5px;width:5px;height:5px;background-color:#c23531;'></span>"
            return [
                param.marker + " " + param.name.charAt(0).toUpperCase() + param.name.slice(1) + ": ",
                param_smaller  + " " + "Upper: " + param.data[5],
                param_smaller  + " " +  "Q3: " + param.data[4],
                param_smaller  + " " + "Median: " + param.data[3],
                param_smaller  + " " + "Q1: " + param.data[2],
                param_smaller  + " " + "Lower: " + param.data[1]
            ].join("<br/>");
        }
      },

      },
      {
      name: 'Outlier',
      type: 'scatter',
      datasetIndex: 2,

      },
      {
      name: 'Mean',
      type: 'scatter',
      datasetIndex: 3,
      symbolSize: 10,
      itemStyle: {
      color: 'red',
      },
      z:10,

      // tooltip: {
      //     formatter: function(param) {
      //         return [
      //             param.marker + "Mean:",
      //             + param.data[1]
      //         ].join("<br/>");
      //     }
      // },


      }

      ]
};

  optionBoxPlotOld: any = {
    title: [
      {
        text: 'Michelson-Morley Experiment',
        left: 'center'
      },
      {
        text: 'upper: Q3 + 1.5 * IQR \nlower: Q1 - 1.5 * IQR',
        borderColor: '#999',
        borderWidth: 1,
        textStyle: {
          fontWeight: 'normal',
          fontSize: 14,
          lineHeight: 20
        },
        left: '10%',
        top: '90%'
      }
    ],
    dataset: [
      {
        // prettier-ignore
        source: [
          [850, 740, 900, 1070, 930, 850, 950, 980, 980, 880, 1000, 980, 930, 650, 760, 810, 1000, 1000, 960, 960],
          [960, 940, 960, 940, 880, 800, 850, 880, 900, 840, 830, 790, 810, 880, 880, 830, 800, 790, 760, 800],
          [880, 880, 880, 860, 720, 720, 620, 860, 970, 950, 880, 910, 850, 870, 840, 840, 850, 840, 840, 840],
          [890, 810, 810, 820, 800, 770, 760, 740, 750, 760, 910, 920, 890, 860, 880, 720, 840, 850, 850, 780],
          [890, 840, 780, 810, 760, 810, 790, 810, 820, 850, 870, 870, 810, 740, 810, 940, 950, 800, 810, 870]
        ]
      },
      {
        transform: {
          type: 'boxplot',
          config: { itemNameFormatter: 'expr {value}' }
        }
      },
      {
        fromDatasetIndex: 1,
        fromTransformResult: 1
      },

    ],
    toolbox: {
      feature: {
        dataZoom: {
          yAxisIndex: 'none'
        },
        restore: {},
        saveAsImage: {}
      }
    },
    tooltip: {
      trigger: 'item',
      axisPointer: {
        type: 'cross'
      }
    },
    grid: {
      left: '10%',
      right: '10%',
      bottom: '15%'
    },
    xAxis: {
      type: 'category',
      boundaryGap: true,
      nameGap: 30,
      splitArea: {
        show: false
      },
      splitLine: {
        show: false
      }
    },
    yAxis: {
      type: 'value',
      name: 'km/s minus 299,000',
      splitArea: {
        show: true
      }
    },
    series: [
      {
        name: 'boxplot',
        type: 'boxplot',
        datasetIndex: 1,
        tooltip: {
          formatter: function(param:any) {
            // console.log("param:",param);
              return [
                  "Experiment " + param.name + ": ",
                  "upper: " + param.data[5],
                  "Q3: " + param.data[4],
                  "median: " + param.data[3],
                  "Q1: " + param.data[2],
                  "lower: " + param.data[1]
              ].join("<br/>");
          }
        }
      },
      {
        name: 'outlier',
        type: 'scatter',
        datasetIndex: 2
      }
    ]
  };

  dataAxis: any = [
    'A',
    'B',
    'C',
    'D',
    'E',
    'F',
    'G',
    'H',
    'I',
    'J',
    'K',
    'L',
    'M',
    'N',
    'O',
    'P',
    'Q',
    'R',
    'S',
    'T',
  ];
  data: any = [
    [10, -220],
    [10, 182],
    [15, 191],
    234,
    290,
    330,
    310,
    123,
    442,
    321,
    90,
    149,
    210,
    122,
    133,
    334,
    198,
    123,
    125,
    220,
  ];
  yMax = 500;
  dataShadow = [];

  //   chart: any;





  constructor(private httpClient: HttpClient, private httpService: HttpService) {


  }

  ngOnChanges(changes: SimpleChanges): void {
    // this.spinnerLoading.emit(true);

    if (this.polygon) {
      //se c'è il poligono chiamare altra funzione
        this.spinnerLoadingChild.emit(true);

        this.getDataGraphPolygon();

    } else {
      //se non c'è il poligono chiama this.getDataGraph() classica
      this.spinnerLoadingChild.emit(true);

      this.getDataGraph();
    }

    // console.log("ECHARTS =", echarts);



  }

  ngOnInit() {
    this.isLoading = true;

    // EChartsOption, graphic
    // this.getDataGraph();
    // this.getDataGraphPolygon();

    for (var i = 0, sum = 0; i < this.dataBoxPlot.length; ++i) {
      if (this.dataBoxPlot[i] >= 0) {
        this.positive.push(this.dataBoxPlot[i]);
        this.negative.push('-');
      } else {
        this.positive.push('-');
        this.negative.push(-this.dataBoxPlot[i]);
      }

      // if (i === 0) {
      //   this.help.push(0);
      // } else {
      //   sum += this.dataBoxPlot[i - 1];
      //   if (this.dataBoxPlot[i] < 0) {
      //     this.help.push(sum + this.dataBoxPlot[i]);
      //   } else {
      //     this.help.push(sum);
      //   }
      // }
    }
  }

  ngAfterViewInit() {
    this.myChart = echarts.init(document.getElementById('main') as HTMLDivElement);



  }

  zoomGraphOn(startValue:any, endValue:any){
    //change the value of the graph
    // console.log("zoom start =", startValue);
    // console.log("zoom end =", endValue);

  }



  zoomGraph(startValue:any, endValue:any){
    //change the value of the graph
    // setTimeout(() => {
    // console.log("zoom start =", startValue);
    // console.log("zoom end =", endValue);

    // }, 1000);
  }



  formatDate(d: any) {
    if (this.operation !== "annualDay") {
      //console.log("d",d);
      d = new Date(d);
      //console.log("!= annualDay", d);

    }
    if (this.operation === "annualMonth") {
      //console.log("=== annualMonth");

      return this.months[d.getMonth()];
    }
    else if (this.operation === "annualDay") {
      //console.log("=== annualDay");

      return d;
    }
    else {
      let month = d.getMonth() + 1
      let day = d.getDate()
      let year = d.getFullYear()
      // console.log("Entro qui!!")
      // console.log(day + "/" + month + "/" + year);
      return day + "/" + month + "/" + year;
    }
  }

  getDataGraphPolygon() {
    let data = {
      dataset: this.dataset,
      selVar: this.variable,
      range: this.range ? Math.abs(this.range) : 0,
      latLngObj: this.polygon,
      isIndicator: this.isIndicator,
      parametro_agg: this.extraParam ? this.extraParam.nameExtraParam : null,
      operation: this.operation,
      statistic: this.statistic,
      circleCoords: this.circleCoords,

    }
    // console.log("QUESTO PARAMETRO IN DATA =", data);
    if(this.statistic !== "boxPlot") {
      this.httpService.post('test/dataPolygon', data,
        // { responseType: 'text' }).subscribe((response: any) => {
        ).subscribe((response: any) => {
          // console.log("RES PRIMA DEL PARSE =", response);
          if (typeof response == 'string') {
            response = JSON.parse(response);
          }
          // console.log("RES DOPO IL PARSE =", response);

          let allDataPolygon = response['dataVect'];
          //console.log("allDataPolygon", allDataPolygon);
          let dataBeforeOp = allDataPolygon["dataBeforeOp"] //abbiamo tutte le date e i valori
          let allDates = _.cloneDeep([...dataBeforeOp]) //qui ci sono tutte le date, se le filtriamo e leviamo i duplicati avremo solo
          allDates = allDates.map((el: any) => {
            return el["date_value"]
          })
          allDates = [...new Set(allDates)]; //abbiamo solo le date 20!
          //console.log("allDates", allDates);

          //   var unique = dataBeforeOp["date_value"].filter(function(elem:any, index:any, self: any) {
          //     return index === self.indexOf(elem);
          // })
          //se di queste usiamo lo zoom e prendiamo le date che stanno nello zoom effettuato
          this.myChart.on('dataZoom', () => {
            // console.log("PARAMS: ", params);
            let option = this.myChart.getOption();
            // console.log("OPTIONSSSSSS =", option);
            this.startZoom = option.dataZoom[0].startValue;
            this.endZoom = option.dataZoom[0].endValue;
            let arrayDate = allDates.filter(this.filterElement(allDates[this.startZoom],allDates[this.endZoom]));

            //console.log("Arraydate after filer zoom:",arrayDate);
            let valuesFiltered = dataBeforeOp.map((element:any, index:any) => {
              if (element.date_value && arrayDate.includes(element.date_value) && element.value_0 !== undefined){
                return {"date": element.date_value, "value": element.value_0};
              }
              else {
                return undefined;

              }
            })
            valuesFiltered = valuesFiltered.filter((element: any) => element !== undefined);
            // console.log("valuesFiltered after filer zoom:",valuesFiltered);
            this.statisticCalc.emit({
              dates: arrayDate,
              values: valuesFiltered
            })

          });

          this.meanMedianStdev.emit(allDataPolygon.mean+"_"+allDataPolygon.median+"_"+allDataPolygon.stdev+"_"+allDataPolygon.trend_yr);

          this.dataTablePolygon.emit(allDataPolygon.dataTable);


          if(this.statistic === "min_mean_max" || this.statistic === "min_10thPerc_median_90thPerc_max"){
            //caso di min_mean_max o min_10thPerc..., una linea per ogni statistica

            let allStats = Object.keys(allDataPolygon.dataPol[0]);
            allStats = allStats.filter((stat: any) => stat !== "x");

            allDataPolygon.dataPol.forEach((element: any) => {

                allStats.forEach((stat: any) => {
                    element[stat] = Number(element[stat]);
                });

            });
            // let statsName = this.statistic.split("_");
                this.chartOption = {

                  xAxis: {
                    type: 'category',
                    boundaryGap: false,
                    data: allDataPolygon.dataPol.map((element: any) => element.x)
                  },
                  yAxis: {
                    type: 'value'
                  },

                  tooltip: {
                    trigger: 'axis',
                    formatter: (paramsFormatter: any) => {

                      const tooltipHTML = paramsFormatter.map((param: any) => {
                        let value = param.value;
                        if (value > 10000 || value < 0.001 && value !== 0) {
                          value = value.toExponential().replace(/e\+?/, ' x 10^');
                        }
                        return `${param.marker} ${param.seriesName}: ${value}`;
                      }).join('<br>');

                      return `${paramsFormatter[0].name}<br>${tooltipHTML}`;

                    },
                    transitionDuration: 0.2,
                    axisPointer: {
                      type: 'cross',
                      label: {
                        backgroundColor: '#6a7985'
                      }
                    }
                  },
                  legend: {
                    data: allStats,
                    orient: 'horizontal',
                    itemGap: 70,
                  },
                  grid: {
                    left: '3%',
                    right: '4%',
                    bottom: '3%',
                    containLabel: true
                  },
                  toolbox: {
                    feature: {
                      dataZoom: {
                        yAxisIndex: 'none'
                      },
                      restore: {},
                      saveAsImage: {}
                    }
                  },

                  dataZoom: [
                    {
                      show: true,
                      realtime: true,
                      type: 'inside',
                    },
                  ],
                  series: allStats.map((stat: any) => {
                    return {
                      data: allDataPolygon.dataPol.map((element: any) => element[stat]),
                      name: stat,
                      type: 'line',
                      stack: this.enableArea ? "counts" : "",
                      // stack: "",
                      areaStyle: this.enableArea ? {} : undefined,
                      smooth: false,
                    }
                  })
                  // series: [{
                  //   data: allDataPolygon.dataPol.map((element: any) => element.mean),
                  //   name: "Mean",
                  //   type: 'line',
                  //   stack: 'counts',
                  //   areaStyle: {},
                  //   smooth: true
                  //   },
                  //   {
                  //   data: allDataPolygon.dataPol.map((element: any) => element.min),
                  //   name: "Min",
                  //   type: 'line',
                  //   stack: 'counts',
                  //   areaStyle: {},
                  //   smooth: true
                  // },
                  // {
                  //   data: allDataPolygon.dataPol.map((element: any) => element.max),
                  //   name: "Max",
                  //   type: 'line',
                  //   stack: 'counts',
                  //   areaStyle: {},
                  //   smooth: true
                  // },
                  // ]
                }


          }
          else{

          allDataPolygon.dataPol.forEach((element: any) => {
            /**
             *  Da rivedere qui!!!!!!
             */
            // element.x = this.formatDate(element.x);
            element.y = Number(element.y);
            // if(element.y> 10000) {
            //   element.y = element.y.toExponential().replace(/e\+?/, ' x 10^');
            // }
            // else if(element.y < 0.001) {
            //   element.y = element.y.toExponential().replace(/e\+?/, ' x 10^');
            // }
          });
          let name = this.variable;

          this.chartOption = {

            // title: {
            //       text: name //title of dataset selected,
            // },

            xAxis: {
              type: 'category',
              boundaryGap: false,
              // data: this.dataRes.allData[name].map((element: any) => element.x)
              data: allDataPolygon.dataPol.map((element: any) => element.x)
            },
            yAxis: {
              type: 'value'
            },
            // tooltip: {
            //   trigger: 'item',
            //   showDelay: 0,
            //   transitionDuration: 0.2,
            // },
            tooltip: {
              trigger: 'axis',
              formatter: (paramsFormatter: any) => {

                const tooltipHTML = paramsFormatter.map((param: any) => {
                  let value = param.value;
                  if (value > 10000 || value < 0.001 && value !== 0) {
                    value = value.toExponential().replace(/e\+?/, ' x 10^');
                  }
                  return `${param.marker} ${param.seriesName}: ${value}`;
                }).join('<br>');

                return `${paramsFormatter[0].name}<br>${tooltipHTML}`;

              },
              transitionDuration: 0.2,
              axisPointer: {
                type: 'cross',
                label: {
                  backgroundColor: '#6a7985'
                }
              }
            },
            legend: {
              data: [name]
            },
            grid: {
              left: '3%',
              right: '4%',
              bottom: '3%',
              containLabel: true
            },
            toolbox: {
              feature: {
                dataZoom: {
                  yAxisIndex: 'none'
                },
                restore: {},
                saveAsImage: {}
              }
            },

            dataZoom: [
              {
                show: true,
                realtime: true,
                type: 'inside',
              },

            ],
            series: [{
              data: allDataPolygon.dataPol.map((element: any) => element.y),
              name: name,
              type: 'line',
              stack: 'counts',
              areaStyle: this.enableArea ? {} : undefined,
              smooth: false
            },
          ]
          }
        }
        this.dataTimeExport.emit(allDataPolygon.dataPol);
        this.spinnerLoadingChild.emit(false);
        });
      }
      else {
        this.spinnerLoadingChild.emit(false);
        // this.dataTimeExport.emit([]);
      }


    //   this.httpClient.post('http://localhost:8000/test/dataPolygon', {
    //   dataset: this.selData.get("dataSetSel")?.value.name,
    //   selVar: this.selData.get("dataSetSel")?.value.name.griddap_url !== "" ? this.variableGroup.get("variableControl")?.value : splittedVar,
    //   isIndicator: this.isIndicator ? "true" : "false",
    //   selDate: this.formatDate(this.selectedDate.get("dateSel")?.value),
    //   range: this.value ? Math.abs(this.value) : 0,
    //   latLngObj: polygonsContainingPoint[0].getLatLngs()[0]
    // }).subscribe({
    //   next: (res: any) => {
    //     console.log("RES =", res);
    //     let allDataPolygon = res['dataVect'];
    //     let valuesPol = allDataPolygon[0]; //media dei valori
    //     let datesPol = allDataPolygon[1]; //tutte le date!


    //   },
    //   error: (msg: any) => {
    //     console.log('METADATA ERROR: ', msg);
    //   }

    // });
    // }

  }


  filterElement(min: any, max: any) {
    return function (a: any) {return a >= min && a <= max; };
  }

  getDataGraph() {

    let data = {
      idMeta: this.idMeta,
      variable: this.variable,
      range: this.range ? Math.abs(this.range) : null,
      operation: this.operation,
      context: this.context,
      dimensions: this.dataset.dimensions,
      dateStart: this.dataset.time_start,
      dateEnd: this.dataset.time_end,
      lat: this.latlng.lat,
      lng: this.latlng.lng,
      // lat_max: this.dataset.lat_max,
      // lat_min: this.dataset.lat_min,
      // lng_min: this.dataset.lng_min,
      // lng_max: this.dataset.lng_max
      lat_max: "no",
      lat_min: "no",
      lng_min: "no",
      lng_max: "no"
    }
    // console.log("RANGE: ", this.range);

    /**
     *  DA SPOSTARE SPINNER PER IL GRAFICO E NON PER LA TABLE
     */

    // this.httpService.post('test/dataGraphCanvas', data, { responseType: 'text' }).subscribe(response => {
    this.httpService.post('test/dataGraphCanvas', data).subscribe((response: any) => {
      if (typeof response == 'string') {
        response = JSON.parse(response);
      }
      // console.log("RES FOR GRAPH: ", response);
      this.dataRes = response;

      this.meanMedianStdev.emit(this.dataRes.allData.mean+"_"+this.dataRes.allData.median+"_"+this.dataRes.allData.stdev+"_"+this.dataRes.allData.trend_yr);

      let name = this.dataRes.allData.entries[0];
      if(this.operation === "annualMonth"){
        this.dataRes.allData[name] = this.dataRes.allData[name].reverse();
      }
      this.dataRes.allData[name].forEach((element: any) => {
        element.date = element.x;
        element.x = this.formatDate(element.x);
        element.y = Number(element.y);
        // if(element.y > 10000) {
        //   element.y = element.y.toExponential().replace(/e\+?/, ' x 10^');
        // }
        // else if(element.y < 0.001) {
        //   element.y = element.y.toExponential().replace(/e\+?/, ' x 10^');
        // }
      });
      let arrayAllDateValue = _.cloneDeep(this.dataRes.allData[name]);
      let arrayAllDate = this.dataRes.allData[name].map((element: any) => element.date);
      let arrayAllValue = this.dataRes.allData[name].map((element: any) => element.y);
      // console.log("all date =", arrayAllDate);
      // console.log("all value =", arrayAllValue);


      this.myChart.on('dataZoom', () => {
        // console.log("PARAMS: ", params);
        let option = this.myChart.getOption();
        // console.log("OPTIONSSSSSS =", option);
        this.startZoom = option.dataZoom[0].startValue;
        this.endZoom = option.dataZoom[0].endValue;
        // console.log("startZoom =", this.startZoom);
        // console.log("endZoom =", this.endZoom);
        // console.log("dateStartZoom =", this.dataRes.allData[name][this.startZoom]["date"]);
        // console.log("dateEndZoom =", this.dataRes.allData[name][this.endZoom]["date"]);
        // console.log("valueStartZoom =", this.dataRes.allData[name][this.startZoom]["y"]);
        // console.log("valueEndZoom =", this.dataRes.allData[name][this.endZoom]["y"]);

        let arrayDate = arrayAllDate.filter(this.filterElement(this.dataRes.allData[name][this.startZoom]["date"], this.dataRes.allData[name][this.endZoom]["date"]));

        let arrayValueTest = arrayAllDateValue.map((element: any, index: any) => {
          if(element.date && arrayDate.includes(element.date)){
              // console.log("include date:",element.date)
              // console.log("element.y",element.y)
              return element.y;
          }
        })
        arrayValueTest = arrayValueTest.filter((element: any) => element !== undefined);
        // let arrayValue = arrayAllValue.filter(this.filterElement(this.dataRes.allData[name][this.startZoom]["y"], this.dataRes.allData[name][this.endZoom]["y"]));

        this.statisticCalc.emit({
          dates: arrayDate,
          values: arrayValueTest
        })

      });



      // const yMax = 500;
      // const dataShadow = [];

      // // tslint:disable-next-line: prefer-for-of
      // for (let i = 0; i < this.dataRes.allData[name].map((element: any) => element.y).length; i++) {
      //   dataShadow.push(yMax);
      // }

      this.chartOption = {

        // title: {
        //       text: name //title of dataset selected,
        // },

        xAxis: {
          type: 'category',
          boundaryGap: false,
          data: this.dataRes.allData[name].map((element: any) => element.x)
        },
        yAxis: {
          type: 'value'
        },
        // tooltip: {
        //   trigger: 'item',
        //   showDelay: 0,
        //   transitionDuration: 0.2,
        // },
        toolbox: {
          feature: {
            dataZoom: {
              yAxisIndex: 'none'
            },
            restore: {},
            saveAsImage: {}
          }
        },
        tooltip: {
          trigger: 'axis',
          formatter: (paramsFormatter: any) => {

            const tooltipHTML = paramsFormatter.map((param: any) => {
              let value = param.value;
              if (value > 10000 || value < 0.001 && value !== 0) {
                value = value.toExponential().replace(/e\+?/, ' x 10^');
              }
              return `${param.marker} ${param.seriesName}: ${value}`;
            }).join('<br>');

            return `${paramsFormatter[0].name}<br>${tooltipHTML}`;

          },
          transitionDuration: 0.2,
          axisPointer: {
            type: 'cross',
            label: {
              backgroundColor: '#6a7985'
            }
          }
        },
        legend: {
          data: [name]
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },

        dataZoom: [
          {
            show: true,
            realtime: true,
            type: 'inside',
          },

        ],
        series: [{
          data: this.dataRes.allData[name].map((element: any) => element.y),
          name: name,
          type: 'line',
          stack: 'counts',
          areaStyle: this.enableArea ? {} : undefined,
          smooth: false
        },
        // {
        //   name: 'X-1',
        //   type: 'line',
        //   stack: 'counts',
        //   areaStyle: {},
        //   smooth: true,
        //   data: [2.3, 3.2, 1.01, 1.34, 3.0, 2.30, 2.10]
        // },
      ]
      }

      // this.chartOptionBars = {

      // };


      //   this.chartOptions = {
      //     title: {
      //       text: this.dataset.title //title of dataset selected
      //     },
      //     zoomEnabled: true,
      //     animationEnabled: true,
      //     theme: "light2",
      //     data: [{
      //       type: "line",
      //       //xValueFormatString: "YYYY",
      //       // yValueFormatString: "$#,###.##",
      //       dataPoints: this.dataRes.allData[name]
      //       // [

      //       // ]
      //     }]

      //   };
      // console.log("CHART OPTIONS: ", this.dataRes.allData[name]);
      this.dataTimeExport.emit(this.dataRes.allData[name]);
      this.spinnerLoadingChild.emit(false);


    });
  }

  onChartEvent(event: any, type: string) {
    // console.log('chart event:', event);
    // console.log('chart type:', type);

    // const startTimestamp = event.batch[0].start;
    // const endTimestamp = event.batch[0].end;

  }
  // }


  // enableDisable




}
