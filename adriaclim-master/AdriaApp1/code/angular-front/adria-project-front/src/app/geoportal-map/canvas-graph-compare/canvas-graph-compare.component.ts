import { HttpClient } from '@angular/common/http';
import { Component, EventEmitter, Input, OnChanges, OnInit, Output, SimpleChanges, ViewChild, AfterViewInit} from '@angular/core';
import { EChartsOption, graphic } from 'echarts';
import * as echarts from 'echarts';
import { ElementRef } from '@angular/core';
import { HttpService } from 'src/app/services/http.service';
import * as _ from 'lodash';

@Component({
  selector: 'app-canvas-graph-compare',
  templateUrl: './canvas-graph-compare.component.html',
  styleUrls: ['./canvas-graph-compare.component.scss']
})
export class CanvasGraphCompareComponent implements OnInit, OnChanges, AfterViewInit {

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
  @ViewChild("parent") parentRef!: ElementRef<HTMLElement>;
  myChart: any;
  dateGraphZoom : any[] = [];
  valueGraphZoom : any[] = [];
  months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  seasons : any = {
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
  optionsCompare: EChartsOption = {};
  option: any;
  help: any[] = [];
  positive: any[] = [];
  negative: any[] = [];
  dataRes: any;
  startZoom: any;
  endZoom: any;

  colors = ['#5470C6', '#EE6666'];


  constructor(private httpService: HttpService) { }

  ngOnChanges(changes: SimpleChanges): void {
    // this.spinnerLoading.emit(true);

    // if (this.polygon) {
    //   //se c'è il poligono chiamare altra funzione
    //     this.spinnerLoadingChild.emit(true);

    //     this.getDataGraphPolygonInterval();

    // } else {
      //se non c'è il poligono chiama this.getDataGraph() classica
      this.spinnerLoadingChild.emit(true);
      this.optionsCompare = {
        color: this.colors,
        tooltip: {
          trigger: 'none',
          axisPointer: {
            type: 'cross'
          }
        },
        legend: {},
        grid: {
          top: 70,
          bottom: 50
        },
        xAxis: [
          {
            type: 'category',
            axisTick: {
              alignWithLabel: true
            },
            axisLine: {
              onZero: false,
              lineStyle: {
                color: this.colors[1]
              }
            },
            axisPointer: {
              label: {
                formatter: function (params:any) {
                  return (
                    'Precipitation  ' +
                    params.value +
                    (params.seriesData.length ? '：' + params.seriesData[0].data : '')
                  );
                }
              }
            },
            // prettier-ignore
            data: ['2016-1', '2016-2', '2016-3', '2016-4', '2016-5', '2016-6', '2016-7', '2016-8', '2016-9', '2016-10', '2016-11', '2016-12']
          },
          {
            type: 'category',
            axisTick: {
              alignWithLabel: true
            },
            axisLine: {
              onZero: false,
              lineStyle: {
                color: this.colors[0]
              }
            },
            axisPointer: {
              label: {
                formatter: function (params:any) {
                  return (
                    'Precipitation  ' +
                    params.value +
                    (params.seriesData.length ? '：' + params.seriesData[0].data : '')
                  );
                }
              }
            },
            // prettier-ignore
            data: ['2015-1', '2015-2', '2015-3', '2015-4', '2015-5', '2015-6', '2015-7', '2015-8', '2015-9', '2015-10', '2015-11', '2015-12']
          }
        ],
        yAxis: [
          {
            type: 'value'
          }
        ],
        series: [
          {
            name: 'Precipitation(2015)',
            type: 'line',
            xAxisIndex: 1,
            smooth: true,
            emphasis: {
              focus: 'series'
            },
            data: [
              2.6, 5.9, 9.0, 26.4, 28.7, 70.7, 175.6, 182.2, 48.7, 18.8, 6.0, 2.3
            ]
          },
          {
            name: 'Precipitation(2016)',
            type: 'line',
            smooth: true,
            emphasis: {
              focus: 'series'
            },
            data: [
              3.9, 5.9, 11.1, 18.7, 48.3, 69.2, 231.6, 46.6, 55.4, 18.4, 10.3, 0.7
            ]
          }
        ]
      };

      // this.getDataGraph();
    // }

    // console.log("ECHARTS =", echarts);

  }

  ngOnInit() {
    this.isLoading = true;

  }


  ngAfterViewInit() {
    this.myChart = echarts.init(document.getElementById('main') as HTMLDivElement);
  }

  formatNumber(number:any) {
    const decimalCount = (number.toString().split('.')[1] || '').length;

    if (decimalCount > 2) {
      return number.toFixed(2);
    }

    return number.toString();
  }

  formatDate(d: any) {
    if (this.operation !== "annualDay") {
      d = new Date(d);
    }
    if (this.operation === "annualMonth") {
      return this.months[d.getMonth()];
    }
    else if (this.operation === "annualDay") {
      return d;
    }
    else if(this.operation === "annualSeason"){
      return this.seasons[d.getMonth()];
    }
    else {
      let month = d.getMonth() + 1
      let day = d.getDate()
      let year = d.getFullYear()
      return day + "/" + month + "/" + year;
    }
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

      if (response.allData !== "fuoriWms"){
        if (typeof response == 'string') {
          response = JSON.parse(response);
        }

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
            if(element.date && arrayDate.includes(element.date)){
                return element.y;
            }
          })
          arrayValueTest = arrayValueTest.filter((element: any) => element !== undefined);

          this.statisticCalc.emit({
            dates: arrayDate,
            values: arrayValueTest
          })

        });



        this.chartOption = {

          xAxis: {
            type: 'category',
            boundaryGap: false,
            data: this.dataRes.allData[name].map((element: any) => element.x)
          },
          yAxis: {
            type: 'value'
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
                  // console.log("VALUE = ", value);
                  // console.log("VALUE = ", typeof value);

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


    });
  }

}
