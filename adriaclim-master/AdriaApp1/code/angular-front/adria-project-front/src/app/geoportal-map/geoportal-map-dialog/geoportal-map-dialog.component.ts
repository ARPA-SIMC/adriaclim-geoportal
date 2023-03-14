import { DatePipe } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { AfterViewInit, Component, ElementRef, Inject, ViewChild } from '@angular/core';
import { FormBuilder, FormControl, FormGroup } from '@angular/forms';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { MatPaginator } from '@angular/material/paginator';
import { MatTableDataSource } from '@angular/material/table';
import { Observable } from 'rxjs';
// import * as saveAs from 'file-saver';
import {saveAs} from 'file-saver';
import { HttpService } from 'src/app/services/http.service';

@Component({
  selector: 'app-geoportal-map-dialog',
  templateUrl: './geoportal-map-dialog.component.html',
  styleUrls: ['./geoportal-map-dialog.component.scss']
})
export class GeoportalMapDialogComponent implements AfterViewInit {

  // displayedColumns: string[] = ['time', 'latitude', 'longitude', 'wind10m'];
  displayedColumns: string[] = [];
  dataSource: MatTableDataSource<any> = new MatTableDataSource();

  spinnerLoading = true;

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
  range: any;
  arrayVariable: any;
  extraParamExport: any;


  minRange: any;
  maxRange: any;

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

  optionsGraph = [
    {
      label: "Default Graph",
      value: "default"
    },
    {
      label: "Annual Cycle",
      value: "annual"
    },
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
      value: "percentile_10"
    },
    {
      label: "90th Percentile",
      value: "percentile_90"
    },
    {
      label: "Median",
      value: "median"
    }
  ]

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

  daysToMilliseconds(days:any) {
    return days * 24 * 60 * 60 * 1000;
  }

  hoursToMilliseconds(h:any) {
    return h * 60 * 60 * 1000;
  }

  // bypass ngIf for paginator
  @ViewChild(MatPaginator) set matPaginator(mp: MatPaginator) {
    // console.log("paginator", mp);

    this.paginator = mp;
    this.setDataSourceAttributes();

  }

  algoType: any;
  @ViewChild('metadataTable') myDiv!: ElementRef;
  @ViewChild('graphDiv') graph!: ElementRef;

  constructor(
    private httpService: HttpService,
    public datePipe: DatePipe,
    private httpClient: HttpClient,
    private fb: FormBuilder,
    private dialogRef: MatDialogRef<GeoportalMapDialogComponent>,
    @Inject(MAT_DIALOG_DATA) data: any) {

    this.description = data.description;
    this.success = data.success;
    // this.create = data.create;
    // this.content = data.content;
    // this.element = data.element;
    this.datasetId = data.datasetId;
    this.datasetName = data.datasetName;
    this.openGraph = data.openGraph;

    this.dataset = data.dataset;
    this.latlng = data.latlng;
    this.dateStart = data.dateStart;
    this.dateEnd = data.dateEnd;
    this.variable = data.variable;
    this.arrayVariable = data.arrayVariable;
    this.range = data.range;
    this.extraParamExport = data.extraParamExport;
    // this.start = this.dateStart.getTime();
    // this.end = this.dateEnd.getTime();
    this.stepDate = this.dataset.adriaclim_timeperiod;
    // if(this.stepDate === "monthly"){
    //   //step di un mese
    //   this.stepDate = this.daysToMilliseconds(30);

    // }else if(this.stepDate === "day" || this.stepDate === "daily"){
    //   //step di un giorno.......
    //   this.stepDate = this.daysToMilliseconds(1);


    // }else if(this.stepDate === "yearly"){
    //   //step di un anno
    //   this.stepDate = this.daysToMilliseconds(365);

    // }else if(this.stepDate === "seasonal"){
    //   //step di tre mesi
    //   this.stepDate = this.daysToMilliseconds(90);

    // }else{
    //   //step di tre ore/sei ore ecc.
    //   console.log("TRE ORE,6 ....=",this.stepDate);
    //   //let stepHours = this.stepDate.split("h")[0];
    //   this.stepDate = this.hoursToMilliseconds(stepHours);

    // }
    console.log("DATASET", this.dataset);
    this.form = this.fb.group({
      // cod: new FormControl(this.element.cod_algo_type),
      cod: new FormControl(null),
      operationSel: new FormControl("default"),
      typeSel: new FormControl("csv"),
      minSliderDate: new FormControl(this.dateStart),
      maxSliderDate: new FormControl(this.dateEnd),
      // minSlider
    })
    if (this.dataset) {
      if (this.dataset.dimensions > 3) {
        this.form = this.fb.group({
          // cod: new FormControl(this.element.cod_algo_type),
          cod: new FormControl(null),
          operationSel: new FormControl("default"),
          typeSel: new FormControl("csv"),
          minSliderDate: new FormControl(this.dateStart),
          maxSliderDate: new FormControl(this.dateEnd),
          minSliderRange: new FormControl(this.extraParamExport.minValue),
          maxSliderRange: new FormControl(this.extraParamExport.maxValue),
          // minSlider
        })

      }

    }
  }

  funzioneProva(event: any) {
    console.log("event target value", event.target.value);
    console.log("stepDate", this.stepDate);
    this.stepMilliseconds = this.daysToMilliseconds(30);
    // this.form.get("maxSliderDate")?.setValue(5);
    // this.form.get("maxSliderDate")?.value.getTime();
    // console.log("MAX SLIDER DATE", this.form.get("maxSliderDate")?.value);

    if(event.target.value < this.form.get("maxSliderDate")?.value.getTime()) {

      let parse = new Date(Number(event.target.value));
      console.log("PARSE MIN", parse);
      // parse.setDate(1);
      // parse.setMonth(parse.getMonth() - 1);
      // console.log("PARSE MIN TO STRING", parse.toString());
      this.form.get("maxSliderDate")?.setValue(parse);

    }
    else if(event.target.value > this.form.get("maxSliderDate")?.value.getTime()) {
      let parse = new Date(Number(event.target.value));
      console.log("PARSE MIN", parse);
      // parse.setDate(1);
      // parse.setMonth(parse.getMonth() + 1);
      // console.log("PARSE MIN TO STRING", parse.toString());
      this.form.get("maxSliderDate")?.setValue(parse);
    }

    // if(this.stepDate === "monthly"){
    //   //step di un mese
    //   if(this.form.get("maxSliderDate")?.value){

    //   }
    // }else if(this.stepDate === "day" || this.stepDate === "daily"){
    //   //step di un giorno.......

    // }else if(this.stepDate === "yearly"){
    //   //step di un anno

    // }else if(this.stepDate === "seasonal"){
    //   //step di tre mesi

    // }else{
    //   //step di tre ore/sei ore ecc.
    //   // let stepHours = this.stepDate.split("h")[0];


    // }
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
      this.getGraphTable();

    }
    // this.getAlgoType();
  }

  // getAlgoType() {
  //   this.httpService.post("adminAlgorithmConfiguration", {
  //     call: "algoType",
  //   }).subscribe((res: any) => {
  //     console.log("RESSSSSSSSSSSSS =", res);

  //     this.algoType = res;
  //   })
  // }

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
    this.httpClient.post('http://localhost:8000/test/metadataTable', data, { responseType: 'text' }).subscribe(response => {
      this.myDiv.nativeElement.innerHTML = response;
    });


  }

  getGraphTable() {

    this.spinnerLoading = true;
    let data = {
      idMeta: this.datasetId,
      dimensions: this.dataset.dimensions,
      lat: this.latlng.lat,
      lng: this.latlng.lng,
      dateStart: this.dateStart,
      dateEnd: this.dateEnd,
      variable: this.variable,
      range: this.range ? this.range : null
    }

    this.httpClient.post('http://localhost:8000/test/dataGraphTable', data, { responseType: 'text' }).subscribe(response => {

      this.spinnerLoading = false;
      if (typeof response === 'string') {
        response = JSON.parse(response);
      }
      this.dataTable = response;

      this.displayedColumns = this.dataTable.data.table.columnNames;
      let dim_unit = this.dataTable.data.table.columnUnits[this.dataTable.data.table.columnUnits.length - 1];
      if (dim_unit) {
        this.displayedColumns[this.displayedColumns.length - 1] = this.displayedColumns[this.displayedColumns.length - 1] + " " + dim_unit;
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

    });

  }

  exportData(typeSel:any){

    //COSI FUNZIONA ORA PERò BOH.......
    let erddapUrl : any;

    if(this.dataset.dimensions === 3){
    //url_type = https://erddap-adriaclim.cmcc-opa.eu/erddap/griddap/atm_regional_5215_16d2_473e.csv?wind10m%5B(2050-11-09T00:00:00Z):1:(2050-11-09T00:00:00Z)%5D%5B(90.0):1:(-90.0)%5D%5B(-171.2326):1:(180.4572)%5D
      erddapUrl = "https://erddap-adriaclim.cmcc-opa.eu/erddap/griddap/" + this.datasetId  + typeSel + "?" + this.variable + "%5B(" + this.formatDateExport(this.dateStart) + "):1:(" + this.formatDateExport(this.dateEnd) +")%5D%5B(" + this.latlng.lat + "):1:(" + this.latlng.lat + ")%5D%5B(" + this.latlng.lng +"):1:(" + this.latlng.lng +")%5D"
    }
    else{
       //caso parametro aggiuntivo
       let rangeMin = this.form.get('minSliderRange')?.value;
       let rangeMax = this.form.get('maxSliderRange')?.value;
      //url_type = https://erddap-adriaclim.cmcc-opa.eu/erddap/griddap/atm_regional_1f91_1673_845b.htmlTable?vegetfrac%5B(2005-11-20):1:(2005-11-20T00:00:00Z)%5D%5B(1.0):1:(13.0)%5D%5B(90.0):1:(-90.0)%5D%5B(-171.2326):1:(180.4572)%5D
      erddapUrl = "https://erddap-adriaclim.cmcc-opa.eu/erddap/griddap/" + this.datasetId +  typeSel + "?" + this.variable + "%5B(" + this.formatDateExport(this.dateStart) + "):1:(" + this.formatDateExport(this.dateEnd) +")%5D%5B(" + rangeMin + "):1:(" + rangeMax +")%5D%5B(" + this.latlng.lat + "):1:(" + this.latlng.lat + ")%5D%5B(" + this.latlng.lng +"):1:(" + this.latlng.lng +")%5D"
    }

    const link = document.createElement('a');
    link.setAttribute('target', '_self');
    link.setAttribute('href', erddapUrl);
    link.setAttribute('download', `${this.datasetId}${typeSel}`);
    document.body.appendChild(link);
    link.click();
    link.remove();


  }


  downloadFile(url: any): any {
    console.log("QUI CI ENRO");
    // const headerDict = {
    //   'Access-Control-Allow-Origin': '*',
    // }
    // const requestOptions = {
    //   headers: new Headers(headerDict),
    //   responseType: 'blob'
    // };

    return this.httpClient.get(url, {responseType:'blob',headers:{'Access-Control-Allow-Origin': '*',
                                                                  "Access-Control-Allow-Methods": "GET, POST, PATCH, PUT, DELETE, OPTIONS",
                                                                  "Access-Control-Allow-Headers": "Origin, Content-Type, X-Auth-Token"}});
  }

  download() {
    console.log("INIZIO DOWNLOAD");

    let erddapUrl: any;
    if (this.dataset.dimensions === 3) {
      //url_type = https://erddap-adriaclim.cmcc-opa.eu/erddap/griddap/atm_regional_5215_16d2_473e.csv?wind10m%5B(2050-11-09T00:00:00Z):1:(2050-11-09T00:00:00Z)%5D%5B(90.0):1:(-90.0)%5D%5B(-171.2326):1:(180.4572)%5D
      erddapUrl = "https://erddap-adriaclim.cmcc-opa.eu/erddap/griddap/" + this.datasetId + this.form.get('typeSel')?.value + "?" + this.variable + "%5B(" + this.formatDateExport(this.dateStart) + "):1:(" + this.formatDateExport(this.dateEnd) + ")%5D%5B(" + this.latlng.lat + "):1:(" + this.latlng.lat + ")%5D%5B(" + this.latlng.lng + "):1:(" + this.latlng.lng + ")%5D"
    }
    else {
      //caso parametro aggiuntivo DA FARE!!!
      //url_type = https://erddap-adriaclim.cmcc-opa.eu/erddap/griddap/atm_regional_1f91_1673_845b.htmlTable?vegetfrac%5B(2005-11-20):1:(2005-11-20T00:00:00Z)%5D%5B(1.0):1:(13.0)%5D%5B(90.0):1:(-90.0)%5D%5B(-171.2326):1:(180.4572)%5D
      erddapUrl = "https://erddap-adriaclim.cmcc-opa.eu/erddap/griddap/" + this.datasetId + this.form.get('typeSel')?.value + "?" + this.variable + "%5B(" + this.formatDateExport(this.dateStart) + "):1:(" + this.formatDateExport(this.dateEnd) + ")%5D%5B(" + this.latlng.lat + "):1:(" + this.latlng.lat + ")%5D%5B(" + this.latlng.lng + "):1:(" + this.latlng.lng + ")%5D"
    }
    console.log("ERDDAP URL", erddapUrl);

    this.downloadFile(erddapUrl).subscribe((response: any) => {
      console.log("Before blob===========",response);
      let blob: any = new Blob([response], { type: 'text/json' });
      // const url= window.URL.createObjectURL(blob);
      //window.open(url);
      saveAs(blob, this.datasetId + this.form.get('typeSel')?.value);

      // const a = document.createElement('a');
      // const objectUrl = URL.createObjectURL(blob);
      // a.href = objectUrl;
      // a.download = this.datasetId + "." + this.form.get('typeSel')?.value;
      // a.click();
      // URL.revokeObjectURL(objectUrl);
      console.log("DOWNLOAD CLICK QUI");

    }), (error: any) => console.log('Error downloading the file'),
    () => console.info('File downloaded successfully');
  }


  downloadWithService() {
    let erddapUrl: any;
    if (this.dataset.dimensions === 3) {
      //url_type = https://erddap-adriaclim.cmcc-opa.eu/erddap/griddap/atm_regional_5215_16d2_473e.csv?wind10m%5B(2050-11-09T00:00:00Z):1:(2050-11-09T00:00:00Z)%5D%5B(90.0):1:(-90.0)%5D%5B(-171.2326):1:(180.4572)%5D
      erddapUrl = "https://erddap-adriaclim.cmcc-opa.eu/erddap/griddap/" + this.datasetId + this.form.get('typeSel')?.value + "?" + this.variable + "%5B(" + this.formatDateExport(this.dateStart) + "):1:(" + this.formatDateExport(this.dateEnd) + ")%5D%5B(" + this.latlng.lat + "):1:(" + this.latlng.lat + ")%5D%5B(" + this.latlng.lng + "):1:(" + this.latlng.lng + ")%5D"
    }
    //https://erddap-adriaclim.cmcc-opa.eu/erddap/griddap/atm_regional_4d78_6f74_63bc.json?wind10m%5B(1969-12-30T00:00:00Z):1:(2005-11-20T00:00:00Z)%5D%5B(42.87742828483367):1:(42.87742828483367)%5D%5B(11.656494140625002):1:(11.656494140625002)%5D
    else {
      //caso parametro aggiuntivo DA FARE!!!
      //url_type = https://erddap-adriaclim.cmcc-opa.eu/erddap/griddap/atm_regional_1f91_1673_845b.htmlTable?vegetfrac%5B(2005-11-20):1:(2005-11-20T00:00:00Z)%5D%5B(1.0):1:(13.0)%5D%5B(90.0):1:(-90.0)%5D%5B(-171.2326):1:(180.4572)%5D
      erddapUrl = "https://erddap-adriaclim.cmcc-opa.eu/erddap/griddap/" + this.datasetId + this.form.get('typeSel')?.value + "?" + this.variable + "%5B(" + this.formatDateExport(this.dateStart) + "):1:(" + this.formatDateExport(this.dateEnd) + ")%5D%5B(" + this.latlng.lat + "):1:(" + this.latlng.lat + ")%5D%5B(" + this.latlng.lng + "):1:(" + this.latlng.lng + ")%5D"
    }

    this.httpService.downloadFile().subscribe((response: any) => {
      console.log("RESPONSE DOWNLOAD", response);

      let blob: any = new Blob([response], { type: 'text/json; charset=utf-8' });
      const url= window.URL.createObjectURL(blob);
      saveAs(blob, "employees.json");
    }),

    (error: any) => console.log('Error downloading the file'),
    () => console.info('File downloaded successfully');


  }



}

