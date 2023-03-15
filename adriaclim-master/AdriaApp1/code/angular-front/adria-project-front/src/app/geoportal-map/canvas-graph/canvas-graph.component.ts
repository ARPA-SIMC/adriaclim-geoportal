import { HttpClient } from '@angular/common/http';
import { Component, EventEmitter, Input, OnChanges, OnInit, Output, SimpleChanges } from '@angular/core';
import { EChartsOption } from 'echarts';

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
  @Input() operation: any;
  @Input() context: any;
  @Output() dataTimeExport = new EventEmitter<any>();

  months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul","Aug", "Sep", "Oct", "Nov", "Dec"];
  chartOption: EChartsOption = {};

//   chart: any;


  dataRes: any;


  constructor(private httpClient: HttpClient) { }

  ngOnChanges(changes: SimpleChanges): void {
    this.getDataGraph();

  }

  ngOnInit() {
    this.isLoading = true;
    // this.getDataGraph();
  }



formatDate(d:any){
  if(this.operation === "annual"){
    return this.months[d.getMonth()];
  }else{
    let month = d.getMonth() + 1
    let day = d.getDate()
    let year = d.getFullYear()

    return day + "/" + month + "/" + year;
  }
}

  getDataGraph() {

    let data = {
		idMeta: this.idMeta,
		variable: this.variable,
		range: this.range? Math.abs(this.range) : null,
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
      console.log("RES FOR GRAPH: ", JSON.parse(response));
      if(typeof response == 'string'){
        response = JSON.parse(response);
      }
      this.dataRes = response;

	    let name = this.dataRes.allData.entries[0];
      this.dataRes.allData[name].forEach((element: any) => {
        element.x = this.formatDate(new Date(element.x));
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
            data: [name,'X-1']
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