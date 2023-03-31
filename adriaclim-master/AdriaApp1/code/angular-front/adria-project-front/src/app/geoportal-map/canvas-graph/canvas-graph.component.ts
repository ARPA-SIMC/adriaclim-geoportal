import { HttpClient } from '@angular/common/http';
import { Component, EventEmitter, Input, OnChanges, OnInit, Output, SimpleChanges } from '@angular/core';
import { EChartsOption, graphic } from 'echarts';

@Component({
  selector: 'app-canvas-graph',
  templateUrl: './canvas-graph.component.html',
  styleUrls: ['./canvas-graph.component.scss']
})
export class CanvasGraphComponent implements OnInit, OnChanges {
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
  @Input() context: any;
  @Input() extraParam: any;
  @Output() dataTimeExport = new EventEmitter<any>();

  months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  chartOption: EChartsOption = {};
  chartOptionBars: EChartsOption = {};
  option: any;
  dataBoxPlot = [900, 345, 393, -108, -154, 135, 178, 286, -119, -361, -203];
  help: any[] = [];
  positive: any[] = [];
  negative: any[] = [];

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
        datasetIndex: 1
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


  dataRes: any;


  constructor(private httpClient: HttpClient) { }

  ngOnChanges(changes: SimpleChanges): void {
    if (this.polygon) {
      //se c'è il poligono chiamare altra funzione
      this.getDataGraphPolygon();
    } else {
      //se non c'è il poligono chiama this.getDataGraph() classica
      this.getDataGraph();
    }

  }

  ngOnInit() {
    this.isLoading = true;
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
    else {
      let month = d.getMonth() + 1
      let day = d.getDate()
      let year = d.getFullYear()

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

    }
    this.httpClient.post('http://localhost:8000/test/dataPolygon', data,
      { responseType: 'text' }).subscribe((response: any) => {
        console.log("RES PRIMA DEL PARSE =", response);
        if (typeof response == 'string') {
          response = JSON.parse(response);
        }
        console.log("RES DOPO IL PARSE =", response);

        let allDataPolygon = response['dataVect'];
        console.log("allDataPolygon", allDataPolygon);
        let valuesPol = allDataPolygon[0]; //media dei valori
        let datesPol = allDataPolygon[1]; //tutte le date!
        console.log("valuesPol", valuesPol);
        console.log("datesPol", datesPol);
        allDataPolygon.forEach((element: any) => {
          element.x = this.formatDate(element.x);
          element.y = Number(element.y);
          if(element.x> 10000) {
            element.x = element.x.toExponential().replace(/e\+?/, ' x 10^');
          }
          else if(element.x < 0.001) {
            element.x = element.x.toExponential().replace(/e\+?/, ' x 10^');
          }
        });
        let name = this.variable;
        // this.dataRes.allData[name].forEach((element: any) => {
        //   element.x = this.formatDate(element.x);
        //   element.y = Number(element.y);
        //   // if(element.y > 10000) {
        //   //   element.y = element.y.toExponential().replace(/e\+?/, ' x 10^');
        //   // }
        //   // else if(element.y < 0.001) {
        //   //   element.y = element.y.toExponential().replace(/e\+?/, ' x 10^');
        //   // }
        // });

        // // const yMax = 500;
        // // const dataShadow = [];

        // // // tslint:disable-next-line: prefer-for-of
        // // for (let i = 0; i < this.dataRes.allData[name].map((element: any) => element.y).length; i++) {
        // //   dataShadow.push(yMax);
        // // }

        this.chartOption = {

          // title: {
          //       text: name //title of dataset selected,
          // },

          xAxis: {
            type: 'category',
            boundaryGap: false,
            // data: this.dataRes.allData[name].map((element: any) => element.x)
            data: allDataPolygon.map((element: any) => element.x)
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

          dataZoom: [
            {
              type: 'inside',
            },
          ],
          series: [{
            data: allDataPolygon.map((element: any) => element.y),
            name: name,
            type: 'line',
            stack: 'counts',
            areaStyle: {},
            smooth: true
          },
         ]
        }
        this.dataTimeExport.emit(allDataPolygon);

      });

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
    console.log("RANGE: ", this.range);

    this.httpClient.post('http://localhost:8000/test/dataGraphCanvas', data, { responseType: 'text' }).subscribe(response => {
      if (typeof response == 'string') {
        response = JSON.parse(response);
      }
      console.log("RES FOR GRAPH: ", response);
      this.dataRes = response;

      let name = this.dataRes.allData.entries[0];
      this.dataRes.allData[name].forEach((element: any) => {
        element.x = this.formatDate(element.x);
        element.y = Number(element.y);
        // if(element.y > 10000) {
        //   element.y = element.y.toExponential().replace(/e\+?/, ' x 10^');
        // }
        // else if(element.y < 0.001) {
        //   element.y = element.y.toExponential().replace(/e\+?/, ' x 10^');
        // }
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
            type: 'inside',
          },
        ],
        series: [{
          data: this.dataRes.allData[name].map((element: any) => element.y),
          name: name,
          type: 'line',
          stack: 'counts',
          areaStyle: {},
          smooth: true
        },
        {
          name: 'X-1',
          type: 'line',
          stack: 'counts',
          areaStyle: {},
          smooth: true,
          data: [2.3, 3.2, 1.01, 1.34, 3.0, 2.30, 2.10]
        },]
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
      console.log("CHART OPTIONS: ", this.dataRes.allData[name]);
      this.dataTimeExport.emit(this.dataRes.allData[name]);


    });
  }

  onChartEvent(event: any, type: string) {
    console.log('chart event:', type, event);
  }




}
