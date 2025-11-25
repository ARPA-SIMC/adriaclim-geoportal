import { HttpClient, HttpEventType, HttpResponse } from '@angular/common/http';
import { Component, EventEmitter, Input, OnChanges, OnInit, Output, SimpleChanges, ViewChild, AfterViewInit } from '@angular/core';
import { EChartsOption, graphic } from 'echarts';
import * as echarts from 'echarts';
import { ElementRef } from '@angular/core';
import { HttpService } from 'src/app/services/http.service';
import * as _ from 'lodash';
import { interval } from 'rxjs';
import { SpinnerLoaderService } from 'src/app/services/spinner-loader.service';

@Component({
  selector: 'app-canvas-graph',
  templateUrl: './canvas-graph.component.html',
  styleUrls: ['./canvas-graph.component.scss']
})
export class CanvasGraphComponent implements OnInit, OnChanges, AfterViewInit {
  private isLoading = false;
  private suppressProgress = false; // disattiva barra/spinner per l’update corrente

  // isLoading!: boolean;
  @Input() isUpdate: boolean = false;
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
  @Input() dimUnit: string = "";
  @Input() progressBarAtStart: any;
  @Output() meanMedianStdev = new EventEmitter<any>();
  @Output() dataTimeExport = new EventEmitter<any>();
  @Output() dataTablePolygon = new EventEmitter<any>();
  @Output() spinnerLoadingChild = new EventEmitter<any>();
  @Output() progressBarCanvas = new EventEmitter<any>();
  @Output() statisticCalc = new EventEmitter<any>();
  @Output() description = new EventEmitter<any>();
  @Output() progressBar = new EventEmitter<any>();
  
  @Output() fakeProgressStart = new EventEmitter<void>();
  @Output() fakeProgressStop = new EventEmitter<void>();

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

  timeoutProgressBar: any;
  private taskStatusInterval: any = null;


  allDataPolygon: any;

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
  chartAlreadyLoaded: boolean | undefined;

  constructor(private httpClient: HttpClient, private httpService: HttpService, private spinnerService: SpinnerLoaderService) {
  }

  ngOnChanges(changes: SimpleChanges): void {
    console.log("CAMBIO", changes);

    // UPDATE: niente barra/spinner, solo refresh grafico
    if (changes['isUpdate']?.currentValue === true) {
      this.suppressProgress = true;   //blocca barra per questo giro
      if (this.polygon) {
        this.getDataGraphPolygonInterval();
      } else {
        this.getDataGraph();
      }
      return; // NON azzerare qui isUpdate nel figlio
    }

    // CARICAMENTO NORMALE: consentiamo barra/spinner
    this.suppressProgress = false;
    if (this.polygon) {
      this.firstSpinner();
      this.getDataGraphPolygonInterval();
    } else {
      this.firstSpinner();
      this.getDataGraph();
    }
  }



  ngOnInit() {
    console.log("INZIO CANVAS GRAPH")
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
   * Funzione che permette di formattare i numeri visualizzabili con un massimo di 2 cifre decimali
   */
  formatNumber(number: any) {
    const decimalCount = (number.toString().split('.')[1] || '').length;

    if (decimalCount > 2) {
      return number.toFixed(2);
    }

    return number.toString();
  }

  /**
   * Funzione che permette di formattare la data da visualizzare sulla base dell'operazione selezionata
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
    // chiusura poligono se serve
    if (this.polygon && this.polygon.length >= 3) {
      const first = this.polygon[0];
      const last = this.polygon[this.polygon.length - 1];
      if (first.lat !== last.lat || first.lng !== last.lng) {
        this.polygon.push({ lat: first.lat, lng: first.lng });
      }
    }

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
    };

    console.log("DATA IF POLYGON =", data);

    // controllo boxPlot
    if (this.statistic !== "boxPlot") {
      if (this.isLoading) {
        console.log("Caricamento già in corso, ignoro nuova richiesta");
        return;
      }
      this.isLoading = true;

      // solo se NON è update → mostra spinner + barra
      if (!this.isUpdate) {
        this.firstSpinner();
        if (this.context === "one") {
          console.log("[FIGLIO] emetto fakeProgressStart");
          this.fakeProgressStart.emit();
          this.chartAlreadyLoaded = true;
        }
      } else {
        // update → solo spinner
        this.spinnerLoadingChild.emit(true);
        this.spinnerService.spinnerShow = true;
      }

      this.httpService.post('dataset/getDataPolygonNew/', data).subscribe({
        next: (response: any) => {
          console.log("PRIMA RESPONSE", response);
          let taskData = { task_id: response.task_id };

          this.taskStatusInterval = setInterval(() => {
            this.httpService.post('dataset/check_task_status/', taskData).subscribe({
              next: (res: any) => {
                console.log("SECONDA RESPONSE", res);
                let task_status = res.dataVect.status;

                if (task_status === 'SUCCESS') {
                  clearInterval(this.taskStatusInterval);
                  this.taskStatusInterval = null;

                  if (!this.isUpdate) {
                    console.log("[FIGLIO] emetto fakeProgressStop");
                    this.fakeProgressStop.emit();
                  } else {
                    // stop spinner update
                    this.spinnerLoadingChild.emit(false);
                    this.spinnerService.spinnerShow = false;
                  }

                  let task_result = { dataVect: res.dataVect.result };
                  this.getDataGraphPolygon(task_result);
                  this.isLoading = false;
                }
                else if (task_status === 'FAILURE') {
                  clearInterval(this.taskStatusInterval);
                  this.taskStatusInterval = null;

                  if (!this.isUpdate) {
                    console.log("[FIGLIO] emetto fakeProgressStop");
                    this.fakeProgressStop.emit();
                  } else {
                    this.spinnerLoadingChild.emit(false);
                    this.spinnerService.spinnerShow = false;
                  }

                  console.error('Task error:', response.dataVect.error);
                  this.isLoading = false;
                }
                else if (task_status === "PROGRESS" && !this.isUpdate) {
                  let progressBarValue = res.dataVect.progressBar;
                  this.progressBar.emit(progressBarValue);
                }
              },
              error: (err: any) => {
                clearInterval(this.taskStatusInterval);
                this.taskStatusInterval = null;

                if (!this.isUpdate) {
                  console.log("[FIGLIO] emetto fakeProgressStop");
                  this.fakeProgressStop.emit();
                } else {
                  this.spinnerLoadingChild.emit(false);
                  this.spinnerService.spinnerShow = false;
                }

                console.log("ERROR =", err);
                this.isLoading = false;
              }
            });
          }, 2000);
        },
        error: (err: any) => {
          console.error("Errore getDataGraphPolygonInterval:", err);
          this.isLoading = false;
        }
      });
    }

    // --- Ramo BoxPlot aggiornato ---
    else {
      if (this.isLoading) {
        console.log("Caricamento già in corso, ignoro nuova richiesta");
        return;
      }
      this.isLoading = true;

      if (!this.isUpdate) {
      // mostra spinner solo per boxPlot
      if (this.statistic === 'boxPlot') {
        this.firstSpinner();
        console.log("[FIGLIO] emetto fakeProgressStart (boxPlot)");
        this.fakeProgressStart.emit();
      }
    } else {
      if (this.statistic === 'boxPlot') {
        this.spinnerLoadingChild.emit(true);
        this.spinnerService.spinnerShow = true;
      }
    }

      data['statistic'] = "min_10thPerc_median_90thPerc_max";

      this.httpService.post('dataset/getDataPolygonNew/', data).subscribe({
        next: (response: any) => {
          const taskData = { task_id: response.task_id };

          this.taskStatusInterval = setInterval(() => {
            this.httpService.post('dataset/check_task_status/', taskData).subscribe({
              next: (res: any) => {
                console.log("SECONDA RESPONSE (boxPlot)", res);

                const task_status = res?.dataVect?.status;
                const result = res?.dataVect?.result;

                // Stop polling appena finisce
                if (task_status === 'SUCCESS') {
                  clearInterval(this.taskStatusInterval);
                  this.taskStatusInterval = null;

                  // spegni sempre lo spinner
                  if (!this.isUpdate) {
                    this.fakeProgressStop.emit();
                  } else {
                    this.spinnerLoadingChild.emit(false);
                    this.spinnerService.spinnerShow = false;
                  }

                  const result = res?.dataVect?.result;

                  if (result && typeof result === 'object' && Array.isArray(result.dataPol)) {
                    this.data1 = result.dataPol.map((el: any) => {
                      return [
                        el["Minimum"],
                        el["10th Percentile"],
                        el["Median"],
                        el["90th Percentile"],
                        el["Maximum"],
                      ];
                    });

                    const showName = result.dataPol.map((el: any) => [el['x']]);
                    this.quantityBoxPlot = new Set();
                    showName.forEach((element: any) => {
                      this.quantityBoxPlot.add(element[0]);
                    });

                    this.optionBoxPlot = {
                      title: [
                        {
                          text: 'Min, 10th Percentile, Median, 90th Percentile, Max',
                          left: 'center',
                          top: '20px'
                        }
                      ],
                      dataset: [
                        { source: this.data1 },
                        { transform: { type: 'boxplot', config: { itemNameFormatter: (params: any) => params.value } } },
                        { fromDatasetIndex: 1, fromTransformResult: 1 },
                      ],
                      tooltip: { trigger: 'item', axisPointer: { type: 'shadow' } },
                      grid: { left: '10%', right: '10%', bottom: '15%' },
                      xAxis: { type: 'category', data: [...this.quantityBoxPlot] },
                      yAxis: { type: 'value', name: 'Values' },
                      series: [
                        { name: 'Box plot', type: 'boxplot', datasetIndex: 1 },
                        { name: 'Outlier', type: 'scatter', datasetIndex: 2 },
                      ]
                    };
                  } else {
                    console.warn("BoxPlot: risultato non strutturato o vuoto:", result);
                  }

                  this.isLoading = false;

                  // --- FIX: forza spegnimento spinner dopo 1s per sicurezza ---
                  setTimeout(() => {
                    if (!this.isUpdate) {
                      this.fakeProgressStop.emit();
                    } else {
                      this.spinnerLoadingChild.emit(false);
                      this.spinnerService.spinnerShow = false;
                    }
                    console.log("[FIX] Spinner force-stopped after SUCCESS (boxPlot)");
                  }, 1000);
                  // --- END FIX ---
                }

                else if (task_status === 'FAILURE') {
                  clearInterval(this.taskStatusInterval);
                  this.taskStatusInterval = null;

                  if (!this.isUpdate) {
                    this.fakeProgressStop.emit();
                  } else {
                    this.spinnerLoadingChild.emit(false);
                    this.spinnerService.spinnerShow = false;
                  }

                  console.error('Task error (boxPlot):', res);
                  this.isLoading = false;
                }

                // se PROGRESS → continua il polling
                },
                error: (err: any) => {
                  clearInterval(this.taskStatusInterval);
                  this.taskStatusInterval = null;

                  if (!this.isUpdate) {
                    this.fakeProgressStop.emit();
                  } else {
                    this.spinnerLoadingChild.emit(false);
                    this.spinnerService.spinnerShow = false;
                  }

                  console.log("ERROR (boxPlot) =", err);
                  this.isLoading = false;
                }
                });
                }, 2000);
                },
                error: (err: any) => {
                  console.error("Errore boxPlot:", err);

                  // spegni comunque lo spinner se fallisce la prima POST
                  if (!this.isUpdate) {
                    this.fakeProgressStop.emit();
                  } else {
                    this.spinnerLoadingChild.emit(false);
                    this.spinnerService.spinnerShow = false;
                  }
                  this.isLoading = false;
                }
              });
            }
          }


  /**
   * Funzione che permette di mostrare il grafico del poligono
   */
  getDataGraphPolygon(response: any) {

    console.log("VERA RES PER POLIGONO", response);


    if (typeof response == 'string') {
      response = JSON.parse(response);
    }
    if (this.dimUnit === "No") {
      this.dimUnit = "";
    }

    this.allDataPolygon = response['dataVect'];
    // let dataBeforeOp = allDataPolygon["dataBeforeOp"] //abbiamo tutte le date e i valori
    // let dataBeforeOp = _.cloneDeep([...allDataPolygon["dataBeforeOp"]]) //abbiamo tutte le date e i valori
    // console.log("allDataPolygon VERA E PROPRIA", allDataPolygon);
    // let dataPolygonDeep = _.cloneDeep([...allDataPolygon["dataPol"]]);
    let dataInGraph = _.cloneDeep([...this.allDataPolygon["dataPol"]]);
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
    let arrayDataDate = this.allDataPolygon.dataPol.map((el: any) => {
      return el["x"]
    });
    // arrayDataDate = [...new Set(arrayDataDate)];
    let arrayDataValue = this.allDataPolygon.dataPol.map((el: any) => {
      return el["y"]
    });
    // arrayDataValue = [...new Set(arrayDataValue)];
    this.statisticCalc.emit({
      dates: arrayDataDate,
      values: arrayDataValue
    });
    this.meanMedianStdev.emit(this.allDataPolygon.mean + "_" + this.allDataPolygon.median + "_" + this.allDataPolygon.stdev + "_" + this.allDataPolygon.trend_yr);
    this.dataTablePolygon.emit(this.allDataPolygon.dataTable);

    let value = this.allDataPolygon.dataPol.map((element: any) => element.y);
    let minMaxValue = {
      min: Math.min(...value).toFixed(0),
      max: Math.max(...value).toFixed(0)
    }
    if (this.statistic === "min_mean_max" || this.statistic === "min_10thPerc_median_90thPerc_max") {
      //caso di min_mean_max o min_10thPerc..., una linea per ogni statistica

      let allStats = Object.keys(this.allDataPolygon.dataPol[0]);
      allStats = allStats.filter((stat: any) => stat !== "x");

      this.allDataPolygon.dataPol.forEach((element: any) => {

        allStats.forEach((stat: any) => {
          element[stat] = Number(element[stat]);
        });

      });
      let prova = this.allDataPolygon.dataPol.map((element: any) => element.x);

      // let statsName = this.statistic.split("_");
      this.chartOption = {

        xAxis: {
          type: 'category',
          boundaryGap: false,
          data: this.allDataPolygon.dataPol.map((element: any) => {
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
          axisLabel: {
            formatter: (val: any) => {
              return isNaN(Number(this.dimUnit)) && this.dimUnit
                ? `${val} ${this.dimUnit}`
                : `${val}`;
            }
          },
          boundaryGap: [0, '100%'],
          min: this.checkMinValue(),
          max: "dataMax"
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
            data: this.allDataPolygon.dataPol.map((element: any) => this.formatNumber(element[stat])),
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

      this.allDataPolygon.dataPol.forEach((element: any) => {
        // element.x = this.formatDate(element.x);
        element.y = Number(element.y);
      });
      let name = this.variable;

      this.chartOption = {

        xAxis: {
          type: 'category',
          boundaryGap: false,
          data: this.allDataPolygon.dataPol.map((element: any) => {

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
          axisLabel: {
            formatter: (val: any) => {
              // show unit only if it is not a number
              return isNaN(Number(this.dimUnit)) && this.dimUnit
                ? `${val} ${this.dimUnit}`
                : `${val}`;
            }
          },
          boundaryGap: [0, '100%'],
          min: this.checkMinValue(),
          max: "dataMax"
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
          data: this.allDataPolygon.dataPol.map((element: any) => this.formatNumber(element.y)),
          name: name,
          type: 'line',
          stack: 'counts',
          areaStyle: this.enableArea ? {} : undefined,
          smooth: false
        },
        ]
      }
    }

    this.dataTimeExport.emit(this.allDataPolygon.dataPol);
    this.spinnerLoadingChild.emit(false);
    this.spinnerService.spinnerShow = false;
    this.progressBarCanvas.emit(false);

  }
  zoomFunctionGraph(arrayDate: any[], dataInGraph: any[]) {
    throw new Error('Method not implemented.');
  }

  onChartEvent(event: any, nameEvent: any) {

  }

  /**
   * Funzione che permette di filtrare i dati da mostrare sul grafico in base allo zoom effettuato
   */
  filterElement(min: any, max: any) {
    return function (a: any) {
      let p = a >= min && a <= max;
      return p;
    };
  }

  /**
   * Funzione che lancia un timout per progress bar di caricamento per chiamata backend
   */
  timeforProgressBar() {
    let addTime: number = 0;
    const intervalValue = 5000; // Intervallo di 5 secondi

    this.timeoutProgressBar = interval(intervalValue).subscribe(() => {
      addTime += 5; // Aggiungi 5 a addTime
      this.progressBar.emit(addTime);

      if (addTime >= 95) {
        this.timeoutProgressBar.unsubscribe(); // Ferma l'intervallo quando addTime raggiunge o supera 95
      }
    });
  }

  /**
   * Funzione che gestisce i dati ricevuti per mostrare il grafico corrispondente
   */
  getDataGraph() {
    // se unità "No", reset
    if (this.dimUnit === "No") {
      this.dimUnit = "";
    }

    // normalizza le date del dataset
    if (this.dataset.time_start && this.dataset.time_start.includes("T")) {
      const dateStart = new Date(this.dataset.time_start);
      this.dataset.time_start = `${dateStart.getFullYear()}-${(dateStart.getMonth() + 1)
        .toString()
        .padStart(2, '0')}-${dateStart.getDate().toString().padStart(2, '0')}`;
    }
    if (this.dataset.time_end && this.dataset.time_end.includes("T")) {
      const dateEnd = new Date(this.dataset.time_end);
      this.dataset.time_end = `${dateEnd.getFullYear()}-${(dateEnd.getMonth() + 1)
        .toString()
        .padStart(2, '0')}-${dateEnd.getDate().toString().padStart(2, '0')}`;
    }

    const data = {
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
      lat_max: "no",
      lat_min: "no",
      lng_min: "no",
      lng_max: "no"
    };

    if (this.isLoading) {
      console.log("Caricamento già in corso, ignoro nuova richiesta");
      return;
    }
    this.isLoading = true;

    // punto → usavate la progress bar finta
    if (!this.isUpdate) {
      this.timeforProgressBar();
    } else {
      this.spinnerLoadingChild.emit(true);
      this.spinnerService.spinnerShow = true;
    }

    this.httpService.post('dataset/getDataGraphicNewCanvas/', data).subscribe({
      next: (response: any) => {
        console.log("[GRAPH] RESPONSE getDataGraph =", response);

        // caso "fuoriWms"
        if (response.allData === "fuoriWms") {
          if (!this.isUpdate) {
            this.progressBarCanvas.emit(false);
            if (this.timeoutProgressBar) {
              this.timeoutProgressBar.unsubscribe();
            }
          } else {
            this.spinnerLoadingChild.emit(false);
            this.spinnerService.spinnerShow = false;
          }
          this.description.emit("Please select point inside the layer");
          this.isLoading = false;
          return;
        }

        // caso errore testuale dal backend
        if (typeof response === "string") {
          console.warn("[GRAPH] backend ha risposto con errore testuale:", response);
          if (!this.isUpdate) {
            this.progressBarCanvas.emit(false);
            if (this.timeoutProgressBar) {
              this.timeoutProgressBar.unsubscribe();
            }
          } else {
            this.spinnerLoadingChild.emit(false);
            this.spinnerService.spinnerShow = false;
          }
          this.isLoading = false;
          return;
        }

        this.dataRes = response;

        // statistiche
        this.meanMedianStdev.emit(
          this.dataRes.allData.mean +
          "_" + this.dataRes.allData.median +
          "_" + this.dataRes.allData.stdev +
          "_" + this.dataRes.allData.trend_yr
        );

        const name = this.dataRes.allData.entries[0];

        if (!this.dataRes.allData[name]) {
          if (!this.isUpdate) {
            this.progressBarCanvas.emit(false);
            if (this.timeoutProgressBar) {
              this.timeoutProgressBar.unsubscribe();
            }
          } else {
            this.spinnerLoadingChild.emit(false);
            this.spinnerService.spinnerShow = false;
          }
          this.description.emit("Please select point inside the layer");
          this.isLoading = false;
          return;
        }

        const seriesData = this.dataRes.allData[name];

        // ordina per data
        seriesData.sort((a: any, b: any) => {
          const da = new Date(a.x).getTime();
          const db = new Date(b.x).getTime();
          return da - db;
        });

        // rileva se è annuale
        const months = new Set<number>();
        const years = new Set<number>();
        seriesData.forEach((el: any) => {
          const d = new Date(el.x);
          if (!isNaN(d.getTime())) {
            months.add(d.getMonth());
            years.add(d.getFullYear());
          }
        });
        const isPureAnnual = years.size > 1 && months.size === 1;

        // normalizza
        seriesData.forEach((element: any) => {
          element.date = element.x;
          element.y = Number(element.y);

          if (isPureAnnual) {
            const d = new Date(element.x);
            element.x = !isNaN(d.getTime())
              ? d.getFullYear().toString()
              : element.x;
          } else {
            element.x = this.formatDate(element.x) ?? element.x;
          }
        });

        this.chartOption = {
          xAxis: {
            type: 'category',
            boundaryGap: false,
            data: seriesData.map((el: any) => el.x)
          },
          yAxis: {
            type: 'value',
            axisLabel: {
              formatter: `{value} ${this.dimUnit}`
            },
            boundaryGap: [0, '100%'],
            min: this.checkMinValue(),
            max: "dataMax"
          },
          toolbox: {
            feature: {
              dataZoom: { yAxisIndex: 'none' },
              restore: {},
              saveAsImage: {}
            }
          },
          tooltip: {
            trigger: 'axis',
            formatter: (paramsFormatter: any) => {

              // --- FIX annual datasets: show only year in tooltip ---
              if (isPureAnnual && paramsFormatter[0]?.name) {
                paramsFormatter[0].name = paramsFormatter[0].name.substring(paramsFormatter[0].name.length - 4);
              }
              // --- END FIX ---

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
            axisPointer: { type: 'cross', label: { backgroundColor: '#6a7985' } }
          },
          legend: {
            data: [name]
          },
          grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
          dataZoom: [
            { show: true, realtime: true, type: 'inside' },
          ],
          series: [{
            data: seriesData.map((el: any) => this.formatNumber(el.y)),
            name: name,
            type: 'line',
            stack: 'counts',
            areaStyle: this.enableArea ? {} : undefined,
            smooth: false
          }]
        };

        this.dataTimeExport.emit(seriesData);

        // QUI era il buco: spegniamo tutto anche nel flusso "punto"
        if (!this.isUpdate) {
          this.progressBarCanvas.emit(false);
          if (this.timeoutProgressBar) {
            this.timeoutProgressBar.unsubscribe();
          }
          // aggiunta per il vostro spinner globale
          this.spinnerLoadingChild.emit(false);
          this.spinnerService.spinnerShow = false;
        } else {
          this.spinnerLoadingChild.emit(false);
          this.spinnerService.spinnerShow = false;
        }

        this.isLoading = false;
      },
      error: (err: any) => {
        console.error("Errore getDataGraph:", err);
        if (!this.isUpdate) {
          this.progressBarCanvas.emit(false);
          if (this.timeoutProgressBar) {
            this.timeoutProgressBar.unsubscribe();
          }
        } else {
          this.spinnerLoadingChild.emit(false);
          this.spinnerService.spinnerShow = false;
        }
        this.isLoading = false;
      }
    });
  }

  checkMinValue() {
    // console.log("DATA RES = ", this.dataRes);

    let arrayOfValue: any;
    let min: any;

    if (this.dataRes) {
      arrayOfValue = this.dataRes.allData[this.variable].map((element: any) => element.y);

      min = Math.min(...arrayOfValue);
    }
    else {
      arrayOfValue = this.allDataPolygon.dataPol.map((element: any) => element.y);

      min = Math.min(...arrayOfValue);
    }

    if (min > 50) {
      return "dataMin";
    }
    else if (min < -50) {
      return "dataMin";
    }
    else {
      return undefined;
    }

  }

  firstSpinner() {
    if(this.progressBarAtStart) {
      this.spinnerLoadingChild.emit(false);
      this.spinnerService.spinnerShow = false;
    }
    else {
      this.spinnerLoadingChild.emit(true);
      this.spinnerService.spinnerShow = true;
    }
  }

}
