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
  private suppressProgress = false; // Disable spinner for current update

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
  @Output() availableDepthsChange = new EventEmitter<any[]>();
  @Output() selectedDepthChange = new EventEmitter<number>();

  availableDepths: number[] = [];
  selectedDepthFromBackend: number | null = null;

  @ViewChild("parent") parentRef!: ElementRef<HTMLElement>;
  myChart: any;
  dateGraphZoom: any[] = [];
  valueGraphZoom: any[] = [];
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

  // Ignore UI-only changes that must NOT trigger a backend reload
  const ignoredOnlyChanges =
    Object.keys(changes).length === 1 &&
    (changes['progressBarAtStart'] || changes['dimUnit']);

  if (ignoredOnlyChanges) {
    return;
  }

  // Explicit update from parent (e.g. depth change / operation change)
  if (changes['isUpdate']?.currentValue === true) {
    this.suppressProgress = true;

    // Show spinner immediately on update (e.g. depth change)
    this.spinnerLoadingChild.emit(true);
    this.spinnerService.spinnerShow = true;

    if (this.polygon) {
      this.getDataGraphPolygonInterval();
    } else {
      this.getDataGraph();
    }
    return;
  }

  // Trigger normal load only for real data-driving input changes
  const shouldReload =
    !!changes['dataset'] ||
    !!changes['latlng'] ||
    !!changes['variable'] ||
    !!changes['range'] ||
    !!changes['polygon'] ||
    !!changes['operation'] ||
    !!changes['statistic'] ||
    !!changes['enableArea'] ||
    !!changes['context'] ||
    !!changes['isIndicator'];

  if (!shouldReload) {
    return;
  }

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
    this.myChart = echarts.init(this.parentRef.nativeElement);

  }

  /**
 * Format numbers for display with a maximum of 2 decimal places
 */
  formatNumber(number: any) {
    const decimalCount = (number.toString().split('.')[1] || '').length;

    if (decimalCount > 2) {
      return number.toFixed(2);
    }

    return number.toString();
  }

  /**
 * Format the display date based on the selected operation
 */
  // formatDate(d: any) {
  //   if (this.operation !== "annualDay") {
  //     d = new Date(d);
  //   }
  //   if (this.operation === "annualMonth") {
  //     return this.months[d.getMonth()];
  //   }
  //   else if (this.operation === "annualDay") {
  //     return d;
  //   }
  //   else if (this.operation === "annualSeason") {
  //     return this.seasons[d.getMonth()];
  //   }
  //   else {
  //     let month = d.getMonth() + 1
  //     let day = d.getDate()
  //     let year = d.getFullYear()
  //     return day + "/" + month + "/" + year;
  //   }
  // }
  formatDate(d: any) {
    if (this.operation === "annualDay") {
      return d;
    }

    // If the backend already returned a label/string, avoid forcing Date parsing
    if (typeof d === "string") {
      const trimmed = d.trim();

      if (this.operation === "annualMonth") {
        const validMonths = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
        if (validMonths.includes(trimmed)) {
          return trimmed;
        }
      }

      if (this.operation === "annualSeason") {
        const validSeasons = ["Winter", "Spring", "Summer", "Autumn"];
        if (validSeasons.includes(trimmed)) {
          return trimmed;
        }
      }
    }

    const parsedDate = new Date(d);

    if (isNaN(parsedDate.getTime())) {
      return d;
    }

    if (this.operation === "annualMonth") {
      return this.months[parsedDate.getMonth()];
    }
    else if (this.operation === "annualSeason") {
      return this.seasons[parsedDate.getMonth()];
    }
    else {
      let month = parsedDate.getMonth() + 1;
      let day = parsedDate.getDate();
      let year = parsedDate.getFullYear();
      return day + "/" + month + "/" + year;
    }
  }

  getDataGraphPolygonInterval() {
    // Close polygon if needed
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

    // Check boxPlot
    if (this.statistic !== "boxPlot") {
      if (this.isLoading) {
        console.log("Caricamento già in corso, ignoro nuova richiesta");
        return;
      }
      this.isLoading = true;

      // Show spinner and loading bar only if NOT an update
      if (!this.isUpdate) {
        this.firstSpinner();
        if (this.context === "one") {
          console.log("[FIGLIO] emetto fakeProgressStart");
          this.fakeProgressStart.emit();
          this.chartAlreadyLoaded = true;
        }
      } else {
        // Update → spinner only
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

    // --- Updated BoxPlot branch ---
    else {
      if (this.isLoading) {
        console.log("Caricamento già in corso, ignoro nuova richiesta");
        return;
      }
      this.isLoading = true;

      if (!this.isUpdate) {
      // Show spinner only for boxPlot
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

                // Stop polling as soon as it finishes
                if (task_status === 'SUCCESS') {
                  clearInterval(this.taskStatusInterval);
                  this.taskStatusInterval = null;

                  // Always turn off the spinner
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

                  // --- FIX: force spinner shutdown after 1s for safety ---
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

                // If PROGRESS → continue polling
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
                  // Turn off the spinner anyway if the first POST fails
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
 * Display the polygon chart
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
    // Detect "single timestamp" case: all points share the same time.
    // In this case, a time-series line chart is not meaningful.
    const times = (this.allDataPolygon?.dataBeforeOp || [])
      .map((r: any) => r.date_value)
      .filter((t: any) => !!t);

    const uniqueTimes = Array.from(new Set(times));
    const isSingleTimestamp = uniqueTimes.length === 1;

    if (isSingleTimestamp) {
      // Do NOT show mean/median/stdev/trend in the UI for single-timestamp views
      this.meanMedianStdev.emit(null);

      // 1) Pick raw values as best as we can (dataBeforeOp -> dataTable -> dataPol)
      let rawValues: number[] = [];

      if (Array.isArray(this.allDataPolygon?.dataBeforeOp) && this.allDataPolygon.dataBeforeOp.length) {
        rawValues = this.allDataPolygon.dataBeforeOp
          .map((r: any) => Number(r.value_0))
          .filter((v: any) => Number.isFinite(v));
      } else if (Array.isArray(this.allDataPolygon?.dataTable) && this.allDataPolygon.dataTable.length) {
        rawValues = this.allDataPolygon.dataTable
          .map((r: any) => Number(r[this.variable]))
          .filter((v: any) => Number.isFinite(v));
      } else if (Array.isArray(this.allDataPolygon?.dataPol) && this.allDataPolygon.dataPol.length) {
        rawValues = this.allDataPolygon.dataPol
          .map((r: any) => Number(r.y))
          .filter((v: any) => Number.isFinite(v));
      }

      // If we can't compute anything, fall back to the normal flow below
      if (rawValues.length) {
        const stat = this.statistic;

        // If user selected a single aggregate stat, show ONE wide bar (what the client asked for)
        const wantsSingleBar =
          stat === 'min' ||
          stat === 'max' ||
          stat === 'median' ||
          stat === 'avg' ||
          stat === '10thPerc' ||
          stat === '90thPerc';

        if (wantsSingleBar) {
          const sorted = [...rawValues].sort((a, b) => a - b);

          const percentile = (q: number) => {
            const idx = (sorted.length - 1) * q;
            const lo = Math.floor(idx);
            const hi = Math.ceil(idx);
            if (lo === hi) return sorted[lo];
            return sorted[lo] + (sorted[hi] - sorted[lo]) * (idx - lo);
          };

          let aggValue = 0;
          let label = 'Value';

          if (stat === 'min') { aggValue = Math.min(...rawValues); label = 'Min'; }
          else if (stat === 'max') { aggValue = Math.max(...rawValues); label = 'Max'; }
          else if (stat === 'median') { aggValue = percentile(0.5); label = 'Median'; }
          else if (stat === '10thPerc') { aggValue = percentile(0.10); label = '10th Perc'; }
          else if (stat === '90thPerc') { aggValue = percentile(0.90); label = '90th Perc'; }
          else { // avg
            aggValue = rawValues.reduce((s, v) => s + v, 0) / rawValues.length;
            label = 'Mean';
          }

          this.chartOption = {
            xAxis: { type: 'category', data: [label] },
            yAxis: {
              type: 'value',
              axisLabel: {
                formatter: (val: any) =>
                  isNaN(Number(this.dimUnit)) && this.dimUnit ? `${val} ${this.dimUnit}` : `${val}`
              }
            },
            tooltip: { trigger: 'item' },
            grid: { left: '3%', right: '4%', bottom: '10%', containLabel: true },
            series: [{
              name: label,
              type: 'bar',
              barWidth: 80, // wide bar, not infinitesimal
              data: [Number(this.formatNumber(aggValue))]
            }]
          };

          this.dataTimeExport.emit(this.allDataPolygon.dataPol);
          this.spinnerLoadingChild.emit(false);
          this.spinnerService.spinnerShow = false;
          this.progressBarCanvas.emit(false);
          return;
        }

        // --- MULTI-STAT single timestamp (client requirement) ---
        const wantsMultiBars =
          stat === "min_mean_max" ||
          stat === "min_10thPerc_median_90thPerc_max";

        if (wantsMultiBars) {
          const sorted = [...rawValues].sort((a, b) => a - b);

          const percentile = (q: number) => {
            const idx = (sorted.length - 1) * q;
            const lo = Math.floor(idx);
            const hi = Math.ceil(idx);
            if (lo === hi) return sorted[lo];
            return sorted[lo] + (sorted[hi] - sorted[lo]) * (idx - lo);
          };

          const mean = rawValues.reduce((s, v) => s + v, 0) / rawValues.length;

          // Values to plot (single category, multiple series)
          const seriesItems =
            stat === "min_mean_max"
              ? [
                  { name: "Min", value: Math.min(...rawValues) },
                  { name: "Mean", value: mean },
                  { name: "Max", value: Math.max(...rawValues) },
                ]
              : [
                  { name: "Min", value: Math.min(...rawValues) },
                  { name: "10th Perc", value: percentile(0.10) },
                  { name: "Median", value: percentile(0.50) },
                  { name: "90th Perc", value: percentile(0.90) },
                  { name: "Max", value: Math.max(...rawValues) },
                ];

          // One label (single timestamp)
          const timeLabel = uniqueTimes[0] ? this.formatDate(uniqueTimes[0]) : "Value";

          // Make bars visible even when some values coincide:
          // - overlap bars a bit (barGap negative)
          // - different widths and z-order so you can still "see" them behind
          const widths = [70, 56, 44, 34, 26]; // descending
          const baseZ = 10;

          this.chartOption = {
            xAxis: { type: "category", data: [String(timeLabel)] },
            yAxis: {
              type: "value",
              axisLabel: {
                formatter: (val: any) =>
                  isNaN(Number(this.dimUnit)) && this.dimUnit ? `${val} ${this.dimUnit}` : `${val}`,
              },
            },
            tooltip: { trigger: "axis", axisPointer: { type: "shadow" } },
            legend: { data: seriesItems.map(s => s.name) },
            grid: { left: "3%", right: "4%", bottom: "10%", containLabel: true },
            series: seriesItems.map((s, i) => ({
              name: s.name,
              type: "bar",
              data: [Number(this.formatNumber(s.value))],
              barWidth: widths[Math.min(i, widths.length - 1)],
              barGap: "-65%",         // overlap a bit
              barCategoryGap: "40%",  // keeps group compact
              z: baseZ + (seriesItems.length - i), // front/back ordering
            })),
          };

          this.dataTimeExport.emit(this.allDataPolygon.dataPol);
          this.spinnerLoadingChild.emit(false);
          this.spinnerService.spinnerShow = false;
          this.progressBarCanvas.emit(false);
          return;
        }
        // --- END MULTI-STAT ---

        // Otherwise (sum / composite stats), show histogram distribution
        const minV = Math.min(...rawValues);
        const maxV = Math.max(...rawValues);

        // Edge case: all values identical -> single wide bar "Count"
        if (minV === maxV) {
          this.chartOption = {
            xAxis: { type: 'category', data: ['Value'] },
            yAxis: { type: 'value' },
            tooltip: { trigger: 'item' },
            grid: { left: '3%', right: '4%', bottom: '10%', containLabel: true },
            series: [{
              name: 'Count',
              type: 'bar',
              barWidth: 80,
              data: [rawValues.length]
            }]
          };

          this.dataTimeExport.emit(this.allDataPolygon.dataPol);
          this.spinnerLoadingChild.emit(false);
          this.spinnerService.spinnerShow = false;
          this.progressBarCanvas.emit(false);
          return;
        }

        const binCount = 10;
        const binSize = (maxV - minV) / binCount;

        const bins = new Array(binCount).fill(0);
        rawValues.forEach(v => {
          const idx = Math.min(binCount - 1, Math.floor((v - minV) / binSize));
          bins[idx] += 1;
        });

        const labels = bins.map((_, i) => {
          const a = minV + i * binSize;
          const b = minV + (i + 1) * binSize;
          return `${this.formatNumber(a)} – ${this.formatNumber(b)}`;
        });

        this.chartOption = {
          xAxis: {
            type: 'category',
            data: labels,
            axisLabel: { rotate: 30 }
          },
          yAxis: { type: 'value' },
          tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
          grid: { left: '3%', right: '4%', bottom: '12%', containLabel: true },
          series: [{
            name: 'Count',
            type: 'bar',
            data: bins,
            barMaxWidth: 60
          }]
        };

        this.dataTimeExport.emit(this.allDataPolygon.dataPol);
        this.spinnerLoadingChild.emit(false);
        this.spinnerService.spinnerShow = false;
        this.progressBarCanvas.emit(false);
        return;
      }
    }

    let dataInGraph = _.cloneDeep([...this.allDataPolygon["dataPol"]]);
    let allDates = _.cloneDeep([...dataInGraph]);

    allDates = dataInGraph.map((el: any) => {
      return el.x;
    })

    allDates = [...new Set(allDates)]; 
    this.myChart.on('dataZoom', () => {
      let option = this.myChart.getOption();
      this.startZoom = option.dataZoom[0].startValue;
      this.endZoom = option.dataZoom[0].endValue;
      let arrayDate = allDates.filter(this.filterElement(allDates[this.startZoom], allDates[this.endZoom]));
      this.zoomFunctionGraph(arrayDate, dataInGraph);

    });

    let arrayDataDate = this.allDataPolygon.dataPol.map((el: any) => {
      return el["x"]
    });
    let arrayDataValue = this.allDataPolygon.dataPol.map((el: any) => {
      return el["y"]
    });
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

      let allStats = Object.keys(this.allDataPolygon.dataPol[0]);
      allStats = allStats.filter((stat: any) => stat !== "x");

      this.allDataPolygon.dataPol.forEach((element: any) => {

        allStats.forEach((stat: any) => {
          element[stat] = Number(element[stat]);
        });

      });
      let prova = this.allDataPolygon.dataPol.map((element: any) => element.x);
      this.chartOption = {

        xAxis: {
          type: 'category',
          boundaryGap: false,
          data: this.allDataPolygon.dataPol.map((element: any) => {
            let elDate = new Date(element.x).toLocaleDateString();
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
            areaStyle: this.enableArea ? {} : undefined,
            smooth: false,
          }
        })
      }

    }
    else {

      this.allDataPolygon.dataPol.forEach((element: any) => {
        element.y = Number(element.y);
      });
      let name = this.variable;

      this.chartOption = {

        xAxis: {
          type: 'category',
          boundaryGap: false,
          data: this.allDataPolygon.dataPol.map((element: any) => {
            let elDate = new Date(element.x).toLocaleDateString();
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
 * Filter chart data based on the current zoom level
 */
  filterElement(min: any, max: any) {
    return function (a: any) {
      let p = a >= min && a <= max;
      return p;
    };
  }

  /**
 * Start a timeout for the loading progress bar during a backend call
 */
  timeforProgressBar() {
    let addTime: number = 0;
    const intervalValue = 5000;
    this.timeoutProgressBar = interval(intervalValue).subscribe(() => {
      addTime += 5; 
      this.progressBar.emit(addTime);
      if (addTime >= 95) {
        this.timeoutProgressBar.unsubscribe();
      }
    });
  }

  /**
 * Handle the received data to display the corresponding chart
 */
  getDataGraph() {
    if (this.dimUnit === "No") {
      this.dimUnit = "";
    }

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

    if (!this.isUpdate) {
      this.timeforProgressBar();
    } else {
      this.spinnerLoadingChild.emit(true);
      this.spinnerService.spinnerShow = true;
    }

    this.httpService.post('dataset/getDataGraphicNewCanvas/', data).subscribe({
      next: (response: any) => {
        console.log("[GRAPH] RESPONSE getDataGraph =", response);

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
        this.availableDepths = this.dataRes?.allData?.available_depths || [];
        this.selectedDepthFromBackend = this.dataRes?.allData?.selected_depth ?? null;
        this.availableDepthsChange.emit(this.availableDepths);
        if (this.selectedDepthFromBackend !== null) {
          this.selectedDepthChange.emit(this.selectedDepthFromBackend);
        }
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

        const isIrregularStationSeries =
          this.dataset &&
          this.dataset.adriaclim_type === "timeseries" &&
          (this.dataset.dimension_names || "").toLowerCase().includes("depth") &&
          this.dataset.lat_min === this.dataset.lat_max &&
          this.dataset.lng_min === this.dataset.lng_max;

        seriesData.sort((a: any, b: any) => {
          const da = new Date(a.x).getTime();
          const db = new Date(b.x).getTime();
          return da - db;
        });

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

        seriesData.forEach((element: any) => {
          element.date = element.x;
          element.y = Number(element.y);

          if (isPureAnnual && !isIrregularStationSeries) {
            const d = new Date(element.x);
            element.x = !isNaN(d.getTime())
              ? d.getFullYear().toString()
              : element.x;
          } else if (!isIrregularStationSeries) {
            element.x = this.formatDate(element.x) ?? element.x;
          }
        });

        if (Array.isArray(seriesData) && seriesData.length === 1) {
          this.meanMedianStdev.emit(null);

          const singleY = Number(seriesData[0].y);
          const singleX = isIrregularStationSeries
            ? this.formatDate(seriesData[0].date)
            : seriesData[0].x;

          this.chartOption = {
            xAxis: { type: 'category', data: [String(singleX)] },
            yAxis: {
              type: 'value',
              axisLabel: {
                formatter: (val: any) =>
                  isNaN(Number(this.dimUnit)) && this.dimUnit ? `${val} ${this.dimUnit}` : `${val}`
              }
            },
            tooltip: { trigger: 'item' },
            grid: { left: '3%', right: '4%', bottom: '10%', containLabel: true },
            series: [{
              name: name,
              type: 'bar',
              barWidth: 80,
              data: [this.formatNumber(singleY)]
            }]
          };

          this.dataTimeExport.emit(seriesData);

          if (!this.isUpdate) {
            this.progressBarCanvas.emit(false);
            if (this.timeoutProgressBar) this.timeoutProgressBar.unsubscribe();
            this.spinnerLoadingChild.emit(false);
            this.spinnerService.spinnerShow = false;
          } else {
            this.spinnerLoadingChild.emit(false);
            this.spinnerService.spinnerShow = false;
          }

          this.isLoading = false;
          return;
        }

        this.chartOption = {
          xAxis: isIrregularStationSeries
            ? {
                type: 'time',
                boundaryGap: false
              }
            : {
                type: 'category',
                boundaryGap: false,
                data: seriesData.map((el: any) => el.x)
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
              const firstName = isIrregularStationSeries
                ? this.formatDate(paramsFormatter[0]?.value?.[0] || paramsFormatter[0]?.axisValue)
                : paramsFormatter[0]?.name;

              if (isPureAnnual && !isIrregularStationSeries && firstName) {
                const yearOnly = String(firstName).substring(String(firstName).length - 4);
                paramsFormatter[0].name = yearOnly;
              }

              const tooltipHTML = paramsFormatter.map((param: any) => {
                let value: any = isIrregularStationSeries ? Number(param.value[1]) : Number(param.value);

                if (value > 10000 || (value < 0.001 && value !== 0)) {
                  value = value.toExponential().replace(/e\+?/, ' x 10^');
                }

                return `${param.marker} ${param.seriesName}: ${value}`;
              }).join('<br>');

              return `${firstName}<br>${tooltipHTML}`;
            },
            transitionDuration: 0.2,
            axisPointer: {
              type: 'cross',
              label: { backgroundColor: '#6a7985' }
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
            data: isIrregularStationSeries
              ? seriesData.map((el: any) => [el.date, Number(el.y)])
              : seriesData.map((el: any) => this.formatNumber(el.y)),
            name: name,
            type: 'line',
            stack: 'counts',
            areaStyle: this.enableArea ? {} : undefined,
            smooth: false
          }]
        };

        this.dataTimeExport.emit(seriesData);

        if (!this.isUpdate) {
          this.progressBarCanvas.emit(false);
          if (this.timeoutProgressBar) {
            this.timeoutProgressBar.unsubscribe();
          }
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
