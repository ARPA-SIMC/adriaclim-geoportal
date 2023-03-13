import { DatePipe } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { AfterViewInit, Component, ElementRef, Inject, ViewChild } from '@angular/core';
import { FormBuilder, FormControl, FormGroup } from '@angular/forms';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { MatPaginator } from '@angular/material/paginator';
import { MatTableDataSource } from '@angular/material/table';

@Component({
  selector: 'app-geoportal-map-dialog',
  templateUrl: './geoportal-map-dialog.component.html',
  styleUrls: ['./geoportal-map-dialog.component.scss']
})
export class GeoportalMapDialogComponent implements AfterViewInit {

  // displayedColumns: string[] = ['time', 'latitude', 'longitude', 'wind10m'];
  displayedColumns: string[] = [];
  dataSource : MatTableDataSource<any> = new MatTableDataSource();

  spinnerLoading = true;

  // @ViewChild(MatPaginator) paginator!: MatPaginator;
  private paginator!: MatPaginator;
  dataTable: any;

  form!: FormGroup;
  description:string;
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
  variable: any;
  range: any;
  arrayVariable: any;

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
      type:".nccsv",
      label:".nccsv - Download a NetCDF-3-like 7-bit ASCII NCCSV .csv file with COARDS/CF/ACDD metadata."
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

  formatDate(d:any){
    let month = d.getMonth() + 1
    let day = d.getDate()
    let year = d.getFullYear()
    return day + "/" + month + "/" + year;
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
        // this.start = this.dateStart.getTime();
        // this.end = this.dateEnd.getTime();
        this.form = this.fb.group({
          // cod: new FormControl(this.element.cod_algo_type),
          cod: new FormControl(null),
          operationSel: new FormControl("default"),
          typeSel: new FormControl("csv"),
          minSlider: new FormControl(this.dateStart),
          maxSlider: new FormControl(this.dateEnd),

        })


        // if(this.element) {

        // }
        // else {
        //   this.form = this.fb.group({
        //     cod: new FormControl(null),
        //     operationSel: new FormControl("default"),

        //     // des: new FormControl(null),
        //     // ord: new FormControl(null)
        //   })
        // }

    }

  // bypass ngIf for paginator
  setDataSourceAttributes() {
    this.dataSource.paginator = this.paginator;

  }

  ngAfterViewInit(): void {
  }

  ngOnInit() {
    if(!this.openGraph) {
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
      range: this.range? this.range : null
    }



    this.httpClient.post('http://localhost:8000/test/dataGraphTable', data, { responseType: 'text' }).subscribe(response => {

    this.spinnerLoading = false;
    if(typeof response === 'string') {
      response = JSON.parse(response);
    }
    this.dataTable = response;

    this.displayedColumns = this.dataTable.data.table.columnNames;
    let dim_unit = this.dataTable.data.table.columnUnits[this.dataTable.data.table.columnUnits.length - 1];
    if (dim_unit){
      this.displayedColumns[this.displayedColumns.length-1] = this.displayedColumns[this.displayedColumns.length-1] + " " + dim_unit;
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

    if(this.dataTable.data.table.rows.length > 0) {
      this.dataSource = new MatTableDataSource(this.dataTable.data.table.rows);
      // bypass ngIf for paginator
      this.setDataSourceAttributes();
      console.log("paginator", this.paginator);


    }

  });

  }

  exportData(typeSel:any){
    //if this.dimensions === 3:
    //url_type = https://erddap-adriaclim.cmcc-opa.eu/erddap/griddap/atm_regional_5215_16d2_473e.csv?wind10m%5B(2050-11-09T00:00:00Z):1:(2050-11-09T00:00:00Z)%5D%5B(90.0):1:(-90.0)%5D%5B(-171.2326):1:(180.4572)%5D
    //let erddapUrl = "https://erddap-adriaclim.cmcc-opa.eu/erddap/griddap/" + this.datasetId + "/" + typeSel + "?" + this.variable + "%5B(" + this.dateStart + "):1:(" + this.dateEnd +")%5D%5B(" + this.latlng.lat + "):1:(" + this.latlng.lat + ")%5D%5B(" + this.latlng.lng +"):1:(" + this.latlng.lng +")%5D"
    //else:
    //caso parametro aggiuntivo
    //url_type = https://erddap-adriaclim.cmcc-opa.eu/erddap/griddap/atm_regional_1f91_1673_845b.htmlTable?vegetfrac%5B(2005-11-20):1:(2005-11-20T00:00:00Z)%5D%5B(1.0):1:(13.0)%5D%5B(90.0):1:(-90.0)%5D%5B(-171.2326):1:(180.4572)%5D
    //erddapUrl = "https://erddap-adriaclim.cmcc-opa.eu/erddap/griddap/" + this.datasetId + "/" + typeSel + "?" + this.variable + "%5B(" + this.dateStart + "):1:(" + this.dateEnd +")%5D%5B(" + this.latlng.lat + "):1:(" + this.latlng.lat + ")%5D%5B(" + this.latlng.lng +"):1:(" + this.latlng.lng +")%5D"
    //
    //
    //

  }


}
