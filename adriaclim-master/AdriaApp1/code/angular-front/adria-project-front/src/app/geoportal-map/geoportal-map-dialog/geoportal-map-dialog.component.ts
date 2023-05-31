import { DatePipe } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { AfterViewInit, Component, ElementRef, Inject, ViewChild, ChangeDetectorRef, AfterContentChecked } from '@angular/core';
import { FormBuilder, FormControl, FormGroup, Validators } from '@angular/forms';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { MatPaginator } from '@angular/material/paginator';
import { MatTableDataSource } from '@angular/material/table';
import { Observable } from 'rxjs';
// import * as saveAs from 'file-saver';
import { saveAs } from 'file-saver';
import { Options, LabelType } from '@angular-slider/ngx-slider';
import { HttpService } from 'src/app/services/http.service';
import { MatSliderChange } from '@angular/material/slider';
import { MAT_SELECT_CONFIG } from '@angular/material/select';
import { last } from 'lodash';

@Component({
  selector: 'app-geoportal-map-dialog',
  templateUrl: './geoportal-map-dialog.component.html',
  styleUrls: ['./geoportal-map-dialog.component.scss'],
  providers: [
    {
      provide: MAT_SELECT_CONFIG,
      useValue: { overlayPanelClass: 'select-overlay-pane-dialog' }
    }
  ]
})
export class GeoportalMapDialogComponent implements AfterViewInit, AfterContentChecked {



  // displayedColumns: string[] = ['time', 'latitude', 'longitude', 'wind10m'];
  displayedColumns: string[] = [];
  dataSource: MatTableDataSource<any> = new MatTableDataSource();

  spinnerLoading: any = true;

  // @ViewChild(MatPaginator) paginator!: MatPaginator;
  private paginator!: MatPaginator;
  dataTable: any;

  form!: FormGroup;
  description: string;
  // create: boolean;
  success: boolean;
  // content = {};
  // element: any;
  datasetId: string;
  datasetName: string;
  openGraph: any;

  dataset: any;
  latlng: any;
  dateStart: any;
  dateEnd: any;
  stepDate: any;
  stepMilliseconds: any;
  variable: any;
  confronto: any;
  range: any;
  arrayVariable: any;
  extraParamExport: any;
  dataOutputGraph: any[] = [];
  stepDateExport: any;
  stepSizeExport: any;
  dataMinExport: any;
  dataMaxExport: any;
  minValue: any;
  maxValue: any;
  meanValue: any;
  medianValue: any;
  stdevValue: any;
  trendValue: any;
  statCalc: any;
  prodDev = this.httpService.apiUrl === "http://localhost:8000/" ? "dev" : "prod";

  info: any = false;
  // yesInfo = document.getElementById("yesInfo");

  circleCoords: any;

  operation: any = "default";
  statistic: any = "avg";

  // PARAMETRI PER CREAZIONE GRAFICO POLIGONI
  isIndicator: any;
  polygon: any;
  polyExport: any;
  polName: any;

  minRange: any;
  maxRange: any;

  options: Options = {
    floor: 0,
    ceil: 100,
  };

  optionsExtra: Options = {
    floor: 0,
    ceil: 100,
  };

  start: any;
  end: any;

  typeOfExport = [
    {
      type: ".csv",
      label: ".csv - Download a ISO-8859-1 comma-separated text table (line 1: names; line 2: units; ISO 8601 times).",
    },
    {
      type: ".json",
      label: ".json - View a table-like UTF-8 JSON file (missing value = 'null'; times are ISO 8601 strings).",
    },
    {
      type: ".largePdf",
      label: ".largePdf - View a large .pdf image file with a graph or map.",
    },
    {
      type: ".largePng",
      label: ".largePng - View a large .png image file with a graph or map.",
    },
    {
      type: ".mat",
      label: ".mat - Download a MATLAB binary file.",
    },
    {
      type: ".nccsv",
      label: ".nccsv - Download a NetCDF-3-like 7-bit ASCII NCCSV .csv file with COARDS/CF/ACDD metadata."
    },
    {
      type: ".pdf",
      label: ".pdf - View a standard, medium-sized .pdf image file with a graph or map.",
    },
    {
      type: ".png",
      label: ".png - View a standard, medium-sized .png image file with a graph or map.",
    },
    {
      type: ".smallPdf",
      label: ".smallPdf - View a small .pdf image file with a graph or map.",
    },
    {
      type: ".transparentPng",
      label: ".transparentPng - View a .png image file (just the data, without axes, landmask, or legend).",
    },
  ]

  optionTimeScale = [
    {
      label: "Default Graph",
      value: "default"
    },
    {
      label: "Annual Month by Month",
      value: "annualMonth"
    },
    {
      label: "Annual Season by Season",
      value: "annualSeason"
    },
    {
      label: "Annual Day by Day",
      value: "annualDay"
    },

  ]

  optionStatistics = [
    {
      label: "Maximum Value (Moment By Moment)",
      value: "max"
    },
    {
      label: "Minimum Value (Moment By Moment)",
      value: "min"
    },
    {
      label: "Mean Value (Moment By Moment)",
      value: "avg"
    },
    {
      label: "10th Percentile",
      value: "10thPerc"
    },
    {
      label: "90th Percentile",
      value: "90thPerc"
    },
    {
      label: "Median",
      value: "median"
    },
    {
      label: "Sum",
      value: "sum"
    },
    {
      label: "Min, Mean, Max",
      value: "min_mean_max"
    },
    {
      label: "Min, 10th Percentile, Median, 90th Percentile, Max",
      value: "min_10thPerc_median_90thPerc_max"
    },
    {
      label: "Box Plot",
      value: "boxPlot"
    }
  ];


  removeAnnualCycle(o: any): boolean {

    if(this.dataset.adriaclim_timeperiod === "yearly") {
      if(o.value === "annualMonth") {
        return true;
      }
      else if(o.value === "annualDay") {
        return true;
      }
      else if(o.value === "annualSeason"){
        return true;
      }
      else {
        return false;
      }
    }
    else if(this.dataset.adriaclim_timeperiod === "monthly" || this.dataset.adriaclim_timeperiod === "seasonal") {
      if(o.value === "annualDay") {
        return true;
      }
      else {
        return false;
      }
    }
    else {
      return false;
    }

  }

  formatDate(d: any) {
    let month = d.getMonth() + 1
    let day = d.getDate()
    let year = d.getFullYear()
    return day + "/" + month + "/" + year;
  }

  formatDateExport(date: any) {
    var d = new Date(date),
      month = '' + (d.getMonth() + 1),
      day = '' + d.getDate(),
      year = d.getFullYear();

    if (month.length < 2)
      month = '0' + month;
    if (day.length < 2)
      day = '0' + day;

    var first_part = [year, month, day].join('-');
    var second_part = "T00:00:00Z";
    return first_part + second_part;
  }


  // bypass ngIf for paginator
  @ViewChild(MatPaginator) set matPaginator(mp: MatPaginator) {
    // console.log("paginator", mp);

    this.paginator = mp;
    this.setDataSourceAttributes();

  }

  algoType: any;
  // @ViewChild('metadataTable') myDiv!: ElementRef;
  @ViewChild('graphDiv') graph!: ElementRef;

  constructor(
    private changeDetector: ChangeDetectorRef,
    private httpService: HttpService,
    public datePipe: DatePipe,
    private httpClient: HttpClient,
    private fb: FormBuilder,
    private dialogRef: MatDialogRef<GeoportalMapDialogComponent>,
    @Inject(MAT_DIALOG_DATA) data: any) {
    // if(this.yesInfo != null) {
    //   this.yesInfo.style.display = "none";

    // }

    this.description = data.description;
    this.success = data.success;
    // this.create = data.create;
    // this.content = data.content;
    // this.element = data.element;
    this.datasetId = data.datasetId;
    this.datasetName = data.datasetName;
    this.openGraph = data.openGraph;
    this.confronto = data.confronto;

    this.dataset = data.dataset;
    this.latlng = data.latlng;
    this.dateStart = data.dateStart;
    this.dateEnd = data.dateEnd;
    this.variable = data.variable;
    this.arrayVariable = data.arrayVariable;
    this.range = data.range;
    this.extraParamExport = data.extraParamExport;

    // PARAMETRI PER CREAZIONE GRAFICO POLIGONI
    this.isIndicator = data.isIndicator;
    this.polygon = data.polygon;
    this.polyExport = data.polyExport;
    this.polName = data.polName;

    this.circleCoords = data.circleCoords;


    // this.start = this.dateStart.getTime();
    // this.end = this.dateEnd.getTime();
    if (this.dataset) {

      this.stepDate = this.dataset.adriaclim_timeperiod;
    }

    //console.log("DATASET", this.dataset);
    this.form = this.fb.group({
      // cod: new FormControl(this.element.cod_algo_type),
      cod: new FormControl(null),
      operationSel: new FormControl("default"),
      statisticSel: new FormControl("avg"),
      typeSel: new FormControl(this.typeOfExport[0].type),
      varSelected: new FormControl(null, Validators.required),
      enableArea: new FormControl(false),

      meanValue: new FormControl(null),
      medianValue: new FormControl(null),
      stdevValue: new FormControl(null),
      trendValue: new FormControl(null),

      prova: new FormControl(null),
      // minSliderDate: new FormControl(this.dateStart),
      // maxSliderDate: new FormControl(this.dateEnd),
      // minSlider
    })
    if (this.dataset) {
      if (this.dataset.dimensions > 3) {
        this.minRange = this.extraParamExport.minValue.toFixed(4);
        this.maxRange = this.extraParamExport.maxValue.toFixed(4);
        this.optionsExtra = {
          floor: this.extraParamExport.minValue,
          ceil: this.extraParamExport.maxValue,
          step: this.extraParamExport.stepSize.toFixed(4),
          draggableRange: true,
          noSwitching: true,
          translate: (value: number, label: LabelType): string => {
            if (value > 10000 || value < 0.001 && value !== 0) {
              return value.toExponential().replace(/e\+?/, ' x 10^');
            }else{
              return value.toString();
            }
          },
        };

      }

    }
  }

  showInfo() {
    // this.info = !this.info;
    let noInfo = document.getElementById("noInfo");
    let yesInfo = document.getElementById("yesInfo");
    if(noInfo && yesInfo) {
      if(noInfo.style.display == "none") {
        noInfo.style.display = "block";
        yesInfo.style.display = "none";
      }
      else {
        noInfo.style.display = "none";
        yesInfo.style.display = "flex";
      }
    }

  }

  ngAfterContentChecked(): void {
    this.changeDetector.detectChanges();
  }

  // bypass ngIf for paginator
  setDataSourceAttributes() {
    this.dataSource.paginator = this.paginator;

  }

  ngAfterViewInit(): void {
  }

  ngOnInit() {

    if (!this.openGraph) {
      this.getMetadataTable();
      // this.setDataSourceAttributes();

    }
    else {
      // console.log("POLYGON", this.polygon);
      // this.spinnerLoading = false;
      if(!this.polygon) {
        this.getGraphTable();

      }

      // this.removeAnnualCycle();
    }
    // this.getAlgoType();
  }

  save() {
    // if(this.element) {
    //   // this.updateAlgoConfig();
    // }
    // else {
    //   // this.createAlgoConfig();
    // }
    // this.dialogRef.close("ok");
  }

  close() {
    this.dialogRef.close("");
  }

  getMetadataTable() {

    let data = {
      idMeta: this.datasetId
    }
    //console.log("idMeta:",data);
    // this.httpService.post('test/metadataTable', data, { responseType: 'text' }).subscribe(response => {
    this.httpService.post('test/metadataTable', data).subscribe((response: any) => {
        if (typeof response === 'string') {
          response = JSON.parse(response);
        }
        this.dataTable = response;
        // console.log("datatable metadata=======",this.dataTable);

        this.displayedColumns = this.dataTable.metadata.table.columnNames;
        let dim_unit: any;

        if (this.dataTable.metadata.table.columnUnits) {
          dim_unit = this.dataTable.metadata.table.columnUnits[this.dataTable.metadata.table.columnUnits.length - 1];
          this.displayedColumns[this.displayedColumns.length - 1] = this.displayedColumns[this.displayedColumns.length - 1] + " " + dim_unit;
        }
        // this.dataTable.data.table.forEach((el: any) => {
        let objArr: any = {};
        let arr1: any = [];
        // console.log("K = ", k);

        this.dataTable.metadata.table.rows.forEach((arr: any) => {
          objArr = {};

          this.dataTable.metadata.table.columnNames.forEach((key: any, i: number) => {
            objArr[key] = arr[i];

          })
          arr1.push(objArr);

        });
        this.dataTable.metadata.table.rows = [...arr1];

        if (this.dataTable.metadata.table.rows.length > 0) {
          this.dataSource = new MatTableDataSource(this.dataTable.metadata.table.rows);
          // bypass ngIf for paginator
          this.setDataSourceAttributes();


        }
      // this.myDiv.nativeElement.innerHTML = response;
      this.spinnerLoading = false;
    });


  }

  getGraphTable() {
    if (this.dataset) {
      // this.spinnerLoading = true;
      let data = {
        idMeta: this.datasetId,
        dimensions: this.dataset.dimensions,
        lat: this.latlng.lat,
        lng: this.latlng.lng,
        dateStart: this.dateStart,
        dateEnd: this.dateEnd,
        variable: this.variable,
        range: this.range ? Math.abs(this.range) : null
      }
      // console.log("RANGE IN DIALOG ======", this.range);


      // console.log("RANGE IN GETGRAPHTABLE======",this.range);
      //console.log("DATA IN GETGRAPHTABLE======", data);

      // this.httpClient.post('http://localhost:8000/test/dataGraphTable', data, { responseType: 'text' }).subscribe(response => {
      this.httpService.post('test/dataGraphTable', data).subscribe((response:any) => {

        if(response.data !== "fuoriWms") {
          // this.spinnerLoading = false;
          if (typeof response === 'string') {
            response = JSON.parse(response);
          }
          this.dataTable = response;
          // console.log("datatable graph =======", this.dataTable);



          this.displayedColumns = this.dataTable.data.table.columnNames;
          let dim_unit = this.dataTable.data.table.columnUnits[this.dataTable.data.table.columnUnits.length - 1];

          if (dim_unit && dim_unit !== "No" && dim_unit !== "Value not defined" && typeof dim_unit === "string") {
            this.displayedColumns[this.displayedColumns.length - 1] = this.displayedColumns[this.displayedColumns.length - 1] + " [" + dim_unit + "]";
          }
          // this.dataTable.data.table.forEach((el: any) => {
          let objArr: any = {};
          let arr1: any = [];
          // console.log("K = ", k);

          this.dataTable.data.table.rows.forEach((arr: any) => {
            objArr = {};

            this.dataTable.data.table.columnNames.forEach((key: any, i: number) => {
              objArr[key] = arr[i];

            })
            arr1.push(objArr);

          });
          this.dataTable.data.table.rows = [...arr1];

          if (this.dataTable.data.table.rows.length > 0) {
            this.dataSource = new MatTableDataSource(this.dataTable.data.table.rows);
            // bypass ngIf for paginator
            this.setDataSourceAttributes();


          }

        }
        else {
          this.description = "The selected point is outside the WMS coverage";
        }

      });
    }
  }

  createErddapUrl() {
    let prova: any[] = [];
    this.form.get("varSelected")?.value.map((el: any) => {
      prova = el;
    })
    // console.log("PROVA = ", prova);
    // console.log("PROVA FORM = ", this.form.get("varSelected")?.value);

  }

  exportData(typeSel: any) {
    //siamo nel caso del punto

    let erddapUrl: any;
    //COSI FUNZIONA ORA PERò BOH.......
    let latMin: any;
    let latMax: any;
    let lngMax: any;
    let lngMin: any;
    if(this.polygon){
      const corner1 = this.polyExport.getSouthWest();
      const corner2 = this.polyExport.getNorthEast();

      // Get the latitudes and longitudes of the corners
      latMin = corner1.lat;
      lngMin = corner1.lng;
      latMax = corner2.lat;
      lngMax = corner2.lng;
    }
    if(this.dataset.griddap_url !== ""){
         erddapUrl = "https://erddap-adriaclim.cmcc-opa.eu/erddap/griddap/" + this.datasetId + typeSel + "?";
        //https://erddap-adriaclim.cmcc-opa.eu/erddap/griddap/adriaclim_WRF_5e78_b419_ec8a.htmlTable?

        //consecutive_dry_days_index_per_time_period%5B(2036-01-15T21:00:00Z):1:(2036-01-15T21:00:00Z)%5D%5B(37.00147):1:(46.97328)%5D%5B(10.0168):1:(21.98158)%5D,number_of_cdd_periods_with_more_than_5days_per_time_period%5B(2036-01-15T21:00:00Z):1:(2036-01-15T21:00:00Z)%5D%5B(37.00147):1:(46.97328)%5D%5B(10.0168):1:(21.98158)%5D

        let variable: any;
        this.form.get("varSelected")?.value.map((el: any, index: number) => {

          if(index === this.form.get("varSelected")?.value.length || index === 0) {
            variable = el;
          }
          else {

            variable =  "," + el;

          }


          //https://erddap.cmcc-opa.eu/erddap/griddap/MedCordex_IPSL_f042_2fca_cade.csv?fg%5B(2020-01-01T00:00:00Z):1:(2020-01-01T00:00:00Z)%5D%5B(42.8210909111826):1:(42.8210909111826)%5D%5B(11.535644531250002):1:(11.535644531250002)%5D%2Ctxn%5B(2020-01-01T00:00:00Z):1:(2020-01-01T00:00:00Z)%5D%5B(42.8210909111826):1:(42.8210909111826)%5D%5B(11.535644531250002):1:(11.535644531250002)%5Dtxx%5B(2020-01-01T00:00:00Z):1:(2020-01-01T00:00:00Z)%5D%5B(42.8210909111826):1:(42.8210909111826)%5D%5B(11.535644531250002):1:(11.535644531250002)%5D

          if (this.dataset.dimensions === 3) {
            //siamo nel caso di latitude e long
            //va aggiunto controllo su poligono
            //url_type = https://erddap-adriaclim.cmcc-opa.eu/erddap/griddap/atm_regional_5215_16d2_473e.csv?wind10m%5B(2050-11-09T00:00:00Z):1:(2050-11-09T00:00:00Z)%5D%5B(90.0):1:(-90.0)%5D%5B(-171.2326):1:(180.4572)%5D
            if(this.polygon) {

              erddapUrl += variable + "%5B(" + this.formatDateExport(this.minValue) + "):1:(" + this.formatDateExport(this.maxValue) + ")%5D%5B(" + latMin + "):1:(" + latMax + ")%5D%5B(" + lngMin + "):1:(" + lngMax + ")%5D"

            }
            else{
              erddapUrl += variable + "%5B(" + this.formatDateExport(this.minValue) + "):1:(" + this.formatDateExport(this.maxValue) + ")%5D%5B(" + this.latlng.lat + "):1:(" + this.latlng.lat + ")%5D%5B(" + this.latlng.lng + "):1:(" + this.latlng.lng + ")%5D"
            }
          }
          else {
            //caso parametro aggiuntivo
            //va aggiunto controllo su poligono
            let rangeMin = this.minRange;
            let rangeMax = this.maxRange;
            if(this.polygon){
            //url_type = https://erddap-adriaclim.cmcc-opa.eu/erddap/griddap/atm_regional_1f91_1673_845b.htmlTable?vegetfrac%5B(2005-11-20):1:(2005-11-20T00:00:00Z)%5D%5B(1.0):1:(13.0)%5D%5B(90.0):1:(-90.0)%5D%5B(-171.2326):1:(180.4572)%5D
              erddapUrl +=  variable + "%5B(" + this.formatDateExport(this.minValue) + "):1:(" + this.formatDateExport(this.maxValue) + ")%5D%5B(" + rangeMin + "):1:(" + rangeMax + ")%5D%5B(" + latMin + "):1:(" + latMax + ")%5D%5B(" + lngMin + "):1:(" + lngMax + ")%5D"
            }
            else{
              erddapUrl +=  variable + "%5B(" + this.formatDateExport(this.minValue) + "):1:(" + this.formatDateExport(this.maxValue) + ")%5D%5B(" + rangeMin + "):1:(" + rangeMax + ")%5D%5B(" + this.latlng.lat + "):1:(" + this.latlng.lat + ")%5D%5B(" + this.latlng.lng + "):1:(" + this.latlng.lng + ")%5D"

            }
          }

        });
    }else{
      //caso tabledap, dobbiamo costruire il suo url!
      //https://erddap-adriaclim.cmcc-opa.eu/erddap/tabledap/arpav_CDD_seasonal.htmlTable?time%2Clatitude%2Clongitude%2CIndicator&time%3E=2022-11-09&time%3C=2022-11-16&latitude%3E=45.605&latitude%3C=45.605&longitude%3E=12.65&longitude%3C=12.65
      erddapUrl = "https://erddap-adriaclim.cmcc-opa.eu/erddap/tabledap/" + this.datasetId + typeSel + "?";
      let variable_names = this.dataset.variable_names.split(" ");

      variable_names.forEach((variable:any,index:any)=>{
        if(index === variable_names.length-1){
          erddapUrl += variable;
        }else{
          erddapUrl += variable + "%2C";
        }
      });
      if(this.polygon){
        erddapUrl += "&time%3E=" + this.formatDateExport(this.minValue) + "&time%3C=" + this.formatDateExport(this.maxValue) + "&latitude%3E=" + latMin + "&latitude%3C=" + latMax + "&longitude%3E=" + lngMin + "&longitude%3C=" + lngMax;
      }
      else {
        erddapUrl += "&time%3E=" + this.formatDateExport(this.minValue) + "&time%3C=" + this.formatDateExport(this.maxValue) + "&latitude%3E=" + this.latlng.lat + "&latitude%3C=" + this.latlng.lat + "&longitude%3E=" + this.latlng.lng + "&longitude%3C=" + this.latlng.lng;

      }

    }

      const link = document.createElement('a');
      link.setAttribute('target', '_self');
      link.setAttribute('href', erddapUrl);
      link.setAttribute('download', `${this.datasetId}${typeSel}`);
      document.body.appendChild(link);
      link.click();
      link.remove();


  }

  addDataTimeExport(graph: any) {
    // Array di timestamp a partire dalle date presenti in 'graph'
    const timestampArray = graph.map((element: any) => {
      const dateParts = element.x.split('/');

      const date = new Date(Number(dateParts[2]), Number(dateParts[1]) - 1, Number(dateParts[0]));
      return date;
    });

    // Salva la data minima e massima del grafico
    // this.dataMinExport = new Date(Math.min(...timestampArray));
    // this.dataMaxExport = new Date(Math.max(...timestampArray));

    //this.minValue = timestampArray[0].getTime();
    this.minValue = timestampArray[0].getTime();
    this.maxValue = timestampArray[timestampArray.length - 1].getTime();

    this.options = {
      floor: this.dateStart.getTime(),
      ceil: this.dateEnd.getTime(),
      draggableRange: true,
      noSwitching: true,
      stepsArray: timestampArray.map((date: Date) => {
        return { value: date.getTime() };
      }),
      translate: (value: number, label: LabelType): string => {
        return new Date(value).toLocaleDateString('it-IT');
      },
      // combineLabels: (minValue: number, maxValue: number): string => {

      // }
    };

  }


  dataTablePolygon(event: any) {
    //console.log("EVENT", event);
    // this.spinnerLoading = false;
    this.dataTable = event;
    // console.log("datatable graph=======", this.dataTable);

    this.displayedColumns = Object.keys(this.dataTable[0]);
    let lastCol = this.displayedColumns[this.displayedColumns.length - 1];
    // console.log("lastCol", lastCol);
    let dim_unit = this.dataTable[0][this.displayedColumns[this.displayedColumns.length - 1]];
    // console.log("dim_unit", dim_unit);
    if (dim_unit && dim_unit !== "No" && dim_unit !== "Value not defined" && typeof dim_unit === "string" ) {
      this.displayedColumns[this.displayedColumns.length - 1] = this.displayedColumns[this.displayedColumns.length - 1] + " [" + dim_unit + "]";
    }




    // this.dataTable.data.table.forEach((el: any) => {
    let objArr: any = {};
    let arr1: any = [];

    // console.log("K = ", k);

    this.dataTable.forEach((arr: any,index: number) => {
      if (index !== 0){
        objArr = {};

        this.displayedColumns.forEach((key: any, i: number) => {
          if (i === this.displayedColumns.length - 1) {
            //ultima chiave da non cambiare
            objArr[key] = arr[lastCol];
          }else{
            objArr[key] = arr[key];
          }
        })
        arr1.push(objArr);
    }

    });
    this.dataTable = [...arr1];
    this.dataTable.sort((a: any, b: any) => {
      return new Date(a.time).getTime() - new Date(b.time).getTime();
    });

    if (this.dataTable.length > 0) {
      this.dataSource = new MatTableDataSource(this.dataTable);
      //console.log(this.dataSource);
      // bypass ngIf for paginator
      this.setDataSourceAttributes();

    }
  }

  spinnerLoadingChild(event: any) {
    // console.log("EVENT =", event);

    this.spinnerLoading = event;
  }

  meanMedianStdev(event: any){
    let mean_median_stdev = event.split("_");
    // console.log("SONO DENTRO MEAN MEDIAN STDEV EVENT");
    console.log("mean_median_stdev = ", mean_median_stdev);

    //console.log("mean_median_stdev = ", mean_median_stdev)
    // this.meanValue = parseFloat(mean_median_stdev[0]).toFixed(3);
    // this.medianValue = parseFloat(mean_median_stdev[1]).toFixed(3);
    // this.stdevValue = parseFloat(mean_median_stdev[2]).toFixed(3);
    this.expoFormat(mean_median_stdev);
    // this.meanValue = parseFloat(mean_median_stdev[0]).toExponential().replace(/e\+?/, ' x 10^').replace(/(\d+\.\d{3})\d*/,'$1');;
    // this.medianValue = parseFloat(mean_median_stdev[1]).toExponential().replace(/e\+?/, ' x 10^').replace(/(\d+\.\d{3})\d*/,'$1');;
    // this.stdevValue = parseFloat(mean_median_stdev[2]).toExponential().replace(/e\+?/, ' x 10^').replace(/(\d+\.\d{3})\d*/,'$1');;

    // this.trendValue = parseFloat(mean_median_stdev[3]).toExponential().replace(/e\+?/, ' x 10^').replace(/(\d+\.\d{3})\d*/,'$1');
    // if(this.meanValue.includes("x 10^0")) {
    //   this.meanValue = this.meanValue.replace("x 10^0", "");

    // }
    // if(this.medianValue.includes("x 10^0")) {
    //   this.medianValue = this.medianValue.replace("x 10^0", "");

    // }
    // if(this.stdevValue.includes("x 10^0")){
    //   this.stdevValue = this.stdevValue.replace("x 10^0", "");

    // }
    // if(this.trendValue.includes("x 10^0")) {
    //   this.trendValue = this.trendValue.replace("x 10^0", "");
    // }
  }

  expoFormat(mean_median_stdev: any) {

    // Variable version
    console.log("expoFormat mean_median_stdev = ", mean_median_stdev);

    this.meanValue = Number(mean_median_stdev[0]).toFixed(3);
    this.medianValue = Number(mean_median_stdev[1]).toFixed(3);
    this.stdevValue = Number(mean_median_stdev[2]).toFixed(3);
    this.trendValue = Number(mean_median_stdev[3]).toFixed(3);
    if (this.meanValue > 10000 || this.meanValue < 0.001 && this.meanValue != 0){
        this.meanValue = parseFloat(mean_median_stdev[0]).toExponential().replace(/e\+?/, ' x 10^').replace(/(\d+\.\d{3})\d*/,'$1');
      }
    if (this.medianValue > 10000 || this.medianValue < 0.001 && this.medianValue != 0){
      this.medianValue = parseFloat(mean_median_stdev[1]).toExponential().replace(/e\+?/, ' x 10^').replace(/(\d+\.\d{3})\d*/,'$1');
    }
    if (this.stdevValue > 10000 || this.stdevValue < 0.001 && this.stdevValue != 0){
        this.stdevValue = parseFloat(mean_median_stdev[2]).toExponential().replace(/e\+?/, ' x 10^').replace(/(\d+\.\d{3})\d*/,'$1');
    }
    if (this.trendValue > 10000 || this.trendValue < 0.001 && this.trendValue != 0){
      this.trendValue = parseFloat(mean_median_stdev[3]).toExponential().replace(/e\+?/, ' x 10^').replace(/(\d+\.\d{3})\d*/,'$1');
    }
    this.meanValue = parseFloat(mean_median_stdev[0]).toExponential().replace(/e\+?/, ' x 10^').replace(/(\d+\.\d{3})\d*/,'$1');
    this.medianValue = parseFloat(mean_median_stdev[1]).toExponential().replace(/e\+?/, ' x 10^').replace(/(\d+\.\d{3})\d*/,'$1');
    this.stdevValue = parseFloat(mean_median_stdev[2]).toExponential().replace(/e\+?/, ' x 10^').replace(/(\d+\.\d{3})\d*/,'$1');

    this.trendValue = parseFloat(mean_median_stdev[3]).toExponential().replace(/e\+?/, ' x 10^').replace(/(\d+\.\d{3})\d*/,'$1');
    if(this.meanValue.includes("x 10^0")) {
      this.meanValue = this.meanValue.replace("x 10^0", "");

    }
    if(this.medianValue.includes("x 10^0")) {
      this.medianValue = this.medianValue.replace("x 10^0", "");

    }
    if(this.stdevValue.includes("x 10^0")){
        this.stdevValue = this.stdevValue.replace("x 10^0", "");

    }
    if(this.trendValue.includes("x 10^0")) {
      this.trendValue = this.trendValue.replace("x 10^0", "");
    }

    // Form control version
    // this.form.get("meanValue")?.setValue(Number(mean_median_stdev[0]).toFixed(3));
    // this.form.get("medianValue")?.setValue(Number(mean_median_stdev[1]).toFixed(3));
    // this.form.get("stdevValue")?.setValue(Number(mean_median_stdev[2]).toFixed(3));
    // this.form.get("trendValue")?.setValue(Number(mean_median_stdev[3]).toFixed(3));
    // if (this.form.get("meanValue")?.value > 10000 || this.form.get("meanValue")?.value < 0.001 && this.form.get("meanValue")?.value != 0){
    //   this.form.get("meanValue")?.setValue(parseFloat(mean_median_stdev[0]).toExponential().replace(/e\+?/, ' x 10^').replace(/(\d+\.\d{3})\d*/,'$1'));
    // }
    // if (this.form.get("medianValue")?.value > 10000 || this.form.get("medianValue")?.value < 0.001 && this.form.get("medianValue")?.value != 0){
    //   this.form.get("medianValue")?.setValue(parseFloat(mean_median_stdev[1]).toExponential().replace(/e\+?/, ' x 10^').replace(/(\d+\.\d{3})\d*/,'$1'));
    // }
    // if (this.form.get("stdevValue")?.value > 10000 || this.form.get("stdevValue")?.value < 0.001 && this.form.get("stdevValue")?.value != 0){
    //   this.form.get("stdevValue")?.setValue(parseFloat(mean_median_stdev[2]).toExponential().replace(/e\+?/, ' x 10^').replace(/(\d+\.\d{3})\d*/,'$1'))
    // }
    // if (this.form.get("stdevValue")?.value > 10000 || this.form.get("stdevValue")?.value < 0.001 && this.form.get("stdevValue")?.value != 0){
    //   this.form.get("stdevValue")?.setValue(parseFloat(mean_median_stdev[3]).toExponential().replace(/e\+?/, ' x 10^').replace(/(\d+\.\d{3})\d*/,'$1'))
    // }

    // if(this.form.get("meanValue")?.value.includes("x 10^0")) {
    //   this.form.get("meanValue")?.setValue(this.form.get("meanValue")?.value.replace("x 10^0", ""));

    // }
    // if(this.form.get("medianValue")?.value.includes("x 10^0")) {
    //   // this.medianValue = this.medianValue.replace("x 10^0", "");
    //   this.medianValue = this.medianValue.replace("x 10^0", "");
    //   this.form.get("medianValue")?.setValue(this.form.get("medianValue")?.value.replace("x 10^0", ""));
    // }
    // if(this.form.get("stdevValue")?.value.includes("x 10^0")){
    //   this.stdevValue = this.stdevValue.replace("x 10^0", "");
    //   this.form.get("stdevValue")?.setValue(this.form.get("stdevValue")?.value.replace("x 10^0", ""));
    // }
    // if(this.form.get("trendValue")?.value.includes("x 10^0")) {
    //   this.trendValue = this.trendValue.replace("x 10^0", "");
    //   this.form.get("trendValue")?.setValue(this.form.get("trendValue")?.value.replace("x 10^0", ""));
    // }
  }

  sendSelGraphPoly() {
    this.operation = this.form.get('operationSel')?.value;
    this.statistic = this.form.get('statisticSel')?.value;
  }

  statisticCalc(event: any) {
    // console.log("before event:",this.statCalc);
    this.statCalc = event;
    // this.calcStatistics();
    console.log("STAT CALC =", this.statCalc);

    // this.calcStatistics();
  }

  calcStatistics() {
    let data = {
      dates : this.statCalc.dates,
      values: this.statCalc.values,
    }
    console.log("data", data);

    this.httpService.post('test/updateStatistics', data).subscribe({
      next: (res: any) => {
        // console.log("res", res);
        // this.meanValue = res.newValues.mean.toFixed(3);
        // this.medianValue = res.newValues.median.toFixed(3);
        // this.stdevValue = res.newValues.stdev.toFixed(3);
        // this.trendValue = res.newValues.trend.toExponential().replace(/e\+?/, ' x 10^').replace(/(\d+\.\d{3})\d*/,'$1');
        // if(this.trendValue.includes("x 10^0")) {
        //   this.trendValue = this.trendValue.replace("x 10^0", "");
        // }
        let mean_median_stdev = [res.newValues.mean, res.newValues.median, res.newValues.stdev, res.newValues.trend];
        this.expoFormat(mean_median_stdev);
      },

      error: (err: any) => {
        console.log(err);
      }
    });


  }





}

