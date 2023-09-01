import { HttpClient } from '@angular/common/http';
import { Component, EventEmitter, Input, OnChanges, OnInit, Output, SimpleChanges, ViewChild, AfterViewInit } from '@angular/core';
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
  @Input() variable: any;
  @Input() range: any;
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
  @Output() description = new EventEmitter<any>();
  @Output() progressBar = new EventEmitter<any>();
  @ViewChild("parent") parentRef!: ElementRef<HTMLElement>;
  myChart: any;
  dateGraphZoom: any[] = [];
  valueGraphZoom: any[] = [];
  // startValue: any;
  // endValue: any =  (document.getElementById('main') as HTMLDivElement).getEchartsInstance().getOption().dataZoom[0]
  months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  seasons: any = {
    0: "Winter",
    1: "Winter",
    2: "Spring",
    3: "Spring",
    4: "Spring",
    5: "Summer",
    6: "Summer",
    7: "Summer",
    8: "Autumn",
    9: "Autumn",
    10: "Autumn",
    11: "Winter",
  }
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
  data1: any[] = [];
  quantityBoxPlot = new Set();

  optionBoxPlot: any = {
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
        source: this.data1.map((item, index) => {
          const average = item.reduce((prev: any, curr: any) => prev + curr) / item.length;
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
      data: []
    },
    yAxis: {
      type: 'value',
      name: 'Values',
    },
    series: [
      {
        name: 'Box plot',
        type: 'boxplot',
        datasetIndex: 1,

        tooltip: {
          formatter: function (param: any) {
            const param_smaller = "<span style='display:inline-block;margin-bottom:3px; margin-left:18px; border-radius:5px;width:5px;height:5px;background-color:#c23531;'></span>"
            return [
              param.marker + " " + param.name.charAt(0).toUpperCase() + param.name.slice(1) + ": ",
              param_smaller + " " + "Upper: " + param.data[5],
              param_smaller + " " + "Q3: " + param.data[4],
              param_smaller + " " + "Median: " + param.data[3],
              param_smaller + " " + "Q1: " + param.data[2],
              param_smaller + " " + "Lower: " + param.data[1]
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
        z: 10,

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

  constructor(private httpClient: HttpClient, private httpService: HttpService) {

  }

  ngOnChanges(changes: SimpleChanges): void {
    // this.spinnerLoading.emit(true);

    if (this.polygon) {
      //se c'è il poligono chiamare altra funzione
      this.spinnerLoadingChild.emit(true);

      this.getDataGraphPolygonInterval();

    } else {
      //se non c'è il poligono chiama this.getDataGraph() classica
      this.spinnerLoadingChild.emit(true);

      this.getDataGraph();
    }

  }

  ngOnInit() {
    this.isLoading = true;

    // EChartsOption, graphic
    // this.getDataGraph();
    // this.getDataGraphPolygon();

    for (let i = 0, sum = 0; i < this.dataBoxPlot.length; ++i) {
      if (this.dataBoxPlot[i] >= 0) {
        this.positive.push(this.dataBoxPlot[i]);
        this.negative.push('-');
      } else {
        this.positive.push('-');
        this.negative.push(-this.dataBoxPlot[i]);
      }

    }
  }

  ngAfterViewInit() {
    // this.myChart = echarts.init(document.getElementById('main') as HTMLDivElement);
    this.myChart = echarts.init(this.parentRef.nativeElement);

  }

  // zoomGraphOn(startValue: any, endValue: any) {
    //change the value of the graph
    // console.log("zoom start =", startValue);
    // console.log("zoom end =", endValue);

  // }

  // zoomGraph(startValue: any, endValue: any) {
    //change the value of the graph
    // setTimeout(() => {
    // console.log("zoom start =", startValue);
    // console.log("zoom end =", endValue);

    // }, 1000);
  // }

  /**
   * FUNZIONE CHE PERMETTE DI FORMATTARE I NUMERI VISUALIZZABILI CON UN MASSIMO DI 2 CIFRE DECIMALI
   */
  formatNumber(number: any) {
    const decimalCount = (number.toString().split('.')[1] || '').length;

    if (decimalCount > 2) {
      return number.toFixed(2);
    }

    return number.toString();
  }

  /**
   * FUNZIONE CHE PERMETTE DI FORMATTARE LA DATA DA VISUALIZZARE SULLA BASE DELL'OPERAZIONE SELEZIONATA
   */
  formatDate(d: any) {
    if (this.operation !== "annualDay") {
      //console.log("d",d);
      d = new Date(d);
      // console.log("!= annualDay", d);

    }
    if (this.operation === "annualMonth") {
      //console.log("=== annualMonth");

      return this.months[d.getMonth()];
    }
    else if (this.operation === "annualDay") {
      //console.log("=== annualDay");

      return d;
    }
    else if (this.operation === "annualSeason") {
      // console.log("this.season",d);
      return this.seasons[d.getMonth()];
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

  getDataGraphPolygonInterval() {
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
    // console.log("data =", data);

    // send HTTP POST request to Django view function
    if (this.statistic !== "boxPlot") {
      this.httpService.post('test/dataPolygon', data).subscribe((response: any) => {
        // console.log("PRIMA RESPONSE", response);

        // extract task ID from response
        let data = {
          task_id: response.task_id,
        }
        // console.log("task_id =", data)

        // periodically check task status
        let checkTaskStatus = setInterval(() => {
          this.httpService.post('test/check_task_status', data).subscribe({
            next: (res: any) => {

              let task_status = res.dataVect.status;

              if (task_status === 'SUCCESS') {
                clearInterval(checkTaskStatus);
                // task completed successfully, extract and display result
                let task_result = {
                  dataVect: res.dataVect.result,
                };
                this.getDataGraphPolygon(task_result);

                //execute the function to create the graph
              }
              else if (task_status === 'FAILURE') {
                // task failed, display error message
                clearInterval(checkTaskStatus);
                let task_error = response.dataVect.error;
                console.error('Task error:', task_error);
              }
              else if(task_status === "PROGRESS"){
                let progressBarValue = res.dataVect.progressBar;
                this.progressBar.emit(progressBarValue);
              }
            },

            error: (err: any) => {
              clearInterval(checkTaskStatus);
              console.log("ERROR =", err);
            }
          });
        }, 2000);
      });
    } //if statistic !== boxPlot
    else {
      this.spinnerLoadingChild.emit(true);

      data['statistic'] = "min_10thPerc_median_90thPerc_max";

      this.httpService.post('test/dataPolygon', data).subscribe((response: any) => {

        // extract task ID from response
        let data = {
          task_id: response.task_id,
        }

        // periodically check task status
        let checkTaskStatus = setInterval(() => {
          this.httpService.post('test/check_task_status', data).subscribe({
            next: (res: any) => {

              this.data1 = res.dataVect.result.dataPol.map((el: any) => {
                return [
                  el["Minimum"],
                  el["10th Percentile"],
                  el["Median"],
                  el["90th Percentile"],
                  el["Maximum"],

                ]
              });

              let showName = res.dataVect.result.dataPol.map((el: any) => {
                return [
                  el['x']
                ]
              });

              let i = 0;
              this.quantityBoxPlot = new Set();
              showName.forEach((element: any) => {
                // this.quantityBoxPlot.add("Box" + " " + i);
                this.quantityBoxPlot.add(element[0]);
                // this.quantityBoxPlot = [...new Set(this.quantityBoxPlot)];
                i++;

              });

              this.optionBoxPlot = {
                title: [
                  {
                    text: 'Min, 10th Percentile, Median, 90th Percentile, Max',
                    left: 'center',
                    top: '20px'
                  },
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
                      config: {
                        itemNameFormatter: function (params: any) {

                          return params.value;
                        }
                      },
                    }
                  },
                  //datasetindex 2
                  {
                    fromDatasetIndex: 1,
                    fromTransformResult: 1
                  },

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
                  data: [...this.quantityBoxPlot]
                },
                yAxis: {
                  type: 'value',
                  name: 'Values',
                },
                series: [
                  {
                    name: 'Box plot',
                    type: 'boxplot',
                    datasetIndex: 1,

                    tooltip: {
                      formatter: function (param: any) {
                        const param_smaller = "<span style='display:inline-block;margin-bottom:3px; margin-left:18px; border-radius:5px;width:5px;height:5px;background-color:#c23531;'></span>"
                        return [
                          param.marker + " " + param.name.charAt(0).toUpperCase() + param.name.slice(1) + ": ",
                          param_smaller + " " + "Max: " + param.data[5],
                          param_smaller + " " + "90th Percentile: " + param.data[4],
                          param_smaller + " " + "Median: " + param.data[3],
                          param_smaller + " " + "10th Percentile: " + param.data[2],
                          param_smaller + " " + "Min: " + param.data[1]
                        ].join("<br/>");
                      }
                    },

                  },
                  {
                    name: 'Outlier',
                    type: 'scatter',
                    datasetIndex: 2,

                  },

                ]
              };

              this.spinnerLoadingChild.emit(false);

              let task_status = res.dataVect.status;

              if (task_status === 'SUCCESS') {
                // task completed successfully, extract and display result
                clearInterval(checkTaskStatus);

              } else if (task_status === 'FAILURE') {
                // task failed, display error message
                clearInterval(checkTaskStatus);
                let task_error = response.dataVect.error;
                console.error('Task error:', task_error);

              }
            },

            error: (err: any) => {
              console.log("ERROR =", err);
            }
          });
        }, 2000);
      });

      // this.spinnerLoadingChild.emit(false);
    }
  }

  zoomFunctionGraph(allDates: any, dataInGraph: any) {

    // versione nuova
    let valuesFiltered = dataInGraph.map((element: any, index: any) => {
      if (element.x && allDates.includes(element.x) && element.y !== undefined) {
        return element.y;
      }
      else {
        return undefined;
      }
    })

    valuesFiltered = valuesFiltered.filter((element: any) => element !== undefined);

    this.statisticCalc.emit({
      dates: allDates,
      values: valuesFiltered
    })

  }

  /**
   * FUNZIONE CHE PERMETTE DI MOSTRARE IL GRAFICO DEL POLIGONO
   */
  getDataGraphPolygon(response: any) {

    if (typeof response == 'string') {
      response = JSON.parse(response);
    }

    let allDataPolygon = response['dataVect'];
    // let dataBeforeOp = allDataPolygon["dataBeforeOp"] //abbiamo tutte le date e i valori
    // let dataBeforeOp = _.cloneDeep([...allDataPolygon["dataBeforeOp"]]) //abbiamo tutte le date e i valori
    // console.log("allDataPolygon VERA E PROPRIA", allDataPolygon);
    // let dataPolygonDeep = _.cloneDeep([...allDataPolygon["dataPol"]]);
    let dataInGraph = _.cloneDeep([...allDataPolygon["dataPol"]]);
    let allDates = _.cloneDeep([...dataInGraph]) //qui ci sono tutte le date, se le filtriamo e leviamo i duplicati avremo solo

    allDates = dataInGraph.map((el: any) => {
      return el.x;
    })

    // console.log("Before set=========",allDates);
    allDates = [...new Set(allDates)]; //abbiamo solo le date 20!
    // console.log("AllDates======",allDates);
    //se di queste usiamo lo zoom e prendiamo le date che stanno nello zoom effettuato
    //this.zoomFunctionGraph(allDates, dataBeforeOp);
    this.myChart.on('dataZoom', () => {
      let option = this.myChart.getOption();
      // console.log("OPTIONSSSSSS =", option);
      this.startZoom = option.dataZoom[0].startValue;
      this.endZoom = option.dataZoom[0].endValue;
      // console.log("startZoom", this.startZoom, typeof this.startZoom);
      // console.log("endZoom", this.endZoom, typeof this.endZoom);

      let arrayDate = allDates.filter(this.filterElement(allDates[this.startZoom], allDates[this.endZoom]));
      // console.log("arrayDate", arrayDate);

      this.zoomFunctionGraph(arrayDate, dataInGraph);

    });
    // this.meanMedianStdev.emit(this.dataRes.allData.mean+"_"+this.dataRes.allData.median+"_"+this.dataRes.allData.stdev+"_"+this.dataRes.allData.trend_yr);
    // console.log("allDataPolygon", allDataPolygon);

    // this.meanMedianStdev.emit(allDataPolygon.mean+"_"+allDataPolygon.median+"_"+allDataPolygon.stdev+"_"+allDataPolygon.trend_yr);
    let arrayDataDate = allDataPolygon.dataPol.map((el: any) => {
      return el["x"]
    });
    // arrayDataDate = [...new Set(arrayDataDate)];
    let arrayDataValue = allDataPolygon.dataPol.map((el: any) => {
      return el["y"]
    });
    // arrayDataValue = [...new Set(arrayDataValue)];
    this.statisticCalc.emit({
      dates: arrayDataDate,
      values: arrayDataValue
    });
    this.meanMedianStdev.emit(allDataPolygon.mean + "_" + allDataPolygon.median + "_" + allDataPolygon.stdev + "_" + allDataPolygon.trend_yr);
    this.dataTablePolygon.emit(allDataPolygon.dataTable);

    let value = allDataPolygon.dataPol.map((element: any) => element.y);
    let minMaxValue = {
      min: Math.min(...value).toFixed(0),
      max: Math.max(...value).toFixed(0)
    }
    if (this.statistic === "min_mean_max" || this.statistic === "min_10thPerc_median_90thPerc_max") {
      //caso di min_mean_max o min_10thPerc..., una linea per ogni statistica

      let allStats = Object.keys(allDataPolygon.dataPol[0]);
      allStats = allStats.filter((stat: any) => stat !== "x");

      allDataPolygon.dataPol.forEach((element: any) => {

        allStats.forEach((stat: any) => {
          element[stat] = Number(element[stat]);
        });

      });
      let prova = allDataPolygon.dataPol.map((element: any) => element.x);

      // let statsName = this.statistic.split("_");
      this.chartOption = {

        xAxis: {
          type: 'category',
          boundaryGap: false,
          data: allDataPolygon.dataPol.map((element: any) => {
            let elDate = new Date(element.x).toLocaleDateString();
            // console.log("element.x", element.x);

            if (elDate !== "Invalid Date") {
              // console.log("elDate", elDate);
              return elDate;
            }
            else {

              return element.x;
            }
          })
        },
        yAxis: {
          type: 'value',
          // min: minMaxValue.min,
          // max: minMaxValue.max,
        },

        tooltip: {
          trigger: 'axis',
          formatter: (paramsFormatter: any) => {

            const tooltipHTML = paramsFormatter.map((param: any) => {
              let value: any = Number(param.value);
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
            data: allDataPolygon.dataPol.map((element: any) => this.formatNumber(element[stat])),
            name: stat,
            type: 'line',
            stack: this.enableArea ? "counts" : "",
            // stack: "",
            areaStyle: this.enableArea ? {} : undefined,
            smooth: false,
          }
        })
      }

    }
    else {

      allDataPolygon.dataPol.forEach((element: any) => {
        /**
         *  Da rivedere qui!!!!!!
         */
        // element.x = this.formatDate(element.x);
        element.y = Number(element.y);
      });
      let name = this.variable;

      this.chartOption = {

        xAxis: {
          type: 'category',
          boundaryGap: false,
          data: allDataPolygon.dataPol.map((element: any) => {

            // console.log("element.x", element.x);

            let elDate = new Date(element.x).toLocaleDateString();
            if (elDate !== "Invalid Date") {
              // console.log("elDate", elDate);
              return elDate;
            }
            else {

              return element.x;
            }

          })
        },
        yAxis: {
          type: 'value',
          // min: minMaxValue.min,
          // max: minMaxValue.max,
        },
        tooltip: {
          trigger: 'axis',
          formatter: (paramsFormatter: any) => {
            // console.log("PARAMS FORMATTER =", paramsFormatter);

            const tooltipHTML = paramsFormatter.map((param: any) => {
              let value: any = Number(param.value);

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
          data: allDataPolygon.dataPol.map((element: any) => this.formatNumber(element.y)),
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

  }

  onChartEvent(event: any, nameEvent: any) {

  }

  /**
   * FUNZIONE CHE PERMETTE DI FILTRARE I DATI DA MOSTRARE SUL GRAFICO IN BASE ALLO ZOOM EFFETTUATO
   */
  filterElement(min: any, max: any) {
    return function (a: any) {
      let p = a >= min && a <= max;
      return p;
    };
  }

  /**
   * FUNZIONE CHE GESTISCE I DATI RICEVUTI PER MOSTRARE IL GRAFICO CORRISPONDENTE
   */
  getDataGraph() {

    let data = {
      dataset: this.dataset,
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

    // this.httpService.post('test/dataGraphCanvas', data, { responseType: 'text' }).subscribe(response => {
    this.httpService.post('test/dataGraphCanvas', data).subscribe((response: any) => {

      if (response.allData !== "fuoriWms") {
        if (typeof response == 'string') {
          response = JSON.parse(response);
        }
        this.dataRes = response;

        this.meanMedianStdev.emit(this.dataRes.allData.mean + "_" + this.dataRes.allData.median + "_" + this.dataRes.allData.stdev + "_" + this.dataRes.allData.trend_yr);

        let name = this.dataRes.allData.entries[0];
        if (this.operation === "annualMonth") {
          this.dataRes.allData[name] = this.dataRes.allData[name].reverse();
        }
        if(this.dataRes.allData[name]) {
          this.dataRes.allData[name].forEach((element: any) => {
            element.date = element.x;
            if (this.formatDate(element.x) === undefined) {
              element.x = element.x;
            } else {
              element.x = this.formatDate(element.x);
            }
            element.y = Number(element.y);
          });
          let arrayAllDateValue = _.cloneDeep(this.dataRes.allData[name]);
          let arrayAllDate = this.dataRes.allData[name].map((element: any) => element.date);
          let arrayAllValue = this.dataRes.allData[name].map((element: any) => element.y);

          this.myChart.on('dataZoom', () => {
            let option = this.myChart.getOption();
            this.startZoom = option.dataZoom[0].startValue;
            this.endZoom = option.dataZoom[0].endValue;

            let arrayDate = arrayAllDate.filter(this.filterElement(this.dataRes.allData[name][this.startZoom]["date"], this.dataRes.allData[name][this.endZoom]["date"]));

            let arrayValueTest = arrayAllDateValue.map((element: any, index: any) => {
              if (element.date && arrayDate.includes(element.date)) {
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

          let value = this.dataRes.allData[name].map((element: any) => element.y);
          let minMaxValue = {
            min: Math.min(...value).toFixed(0),
            max: Math.max(...value).toFixed(0),
          }
          this.chartOption = {

            xAxis: {
              type: 'category',
              boundaryGap: false,
              // data: this.dataRes.allData[name].map((element: any) => element.x)
              data: this.dataRes.allData[name].map((element: any) => {

                let elDate = new Date(element.x).toLocaleDateString();
                // console.log("elDate", elDate);
                if (elDate !== "Invalid Date") {
                  return elDate;
                }
                else {

                  return element.x;
                }

              })
            },
            yAxis: {
              type: 'value',
              // min: minMaxValue.min,
              // max: minMaxValue.max,
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
            tooltip: {
              trigger: 'axis',
              formatter: (paramsFormatter: any) => {

                const tooltipHTML = paramsFormatter.map((param: any) => {
                  let value: any = Number(param.value);
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
              data: this.dataRes.allData[name].map((element: any) => this.formatNumber(element.y)),
              name: name,
              type: 'line',
              stack: 'counts',
              areaStyle: this.enableArea ? {} : undefined,
              smooth: false
            },
            ]
          }

          this.dataTimeExport.emit(this.dataRes.allData[name]);
          this.spinnerLoadingChild.emit(false);

        }
        else {
          this.spinnerLoadingChild.emit(false);
          this.description.emit("Please select point inside the layer");

        }
      }

    });
  }

}
