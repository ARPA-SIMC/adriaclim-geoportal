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

  displayedColumns: string[] = ['time', 'latitude', 'longitude', 'wind10m'];
  dataSource: any;

  spinnerLoading = true;

  @ViewChild(MatPaginator) paginator!: MatPaginator;
  dataTable: any;

  form!: FormGroup;
  description:string;
  // create: boolean;
  success: boolean;
  // content = {};
  element: any;
  datasetId: string;
  datasetName: string;
  openGraph: any;

  dataset: any;
  latlng: any;
  dateStart: any;
  dateEnd: any;
  variable: any;
  range: any;

  algoType: any;
  @ViewChild('metadataTable') myDiv!: ElementRef;
  @ViewChild('graphDiv') graph!: ElementRef;

    constructor(
        private httpClient: HttpClient,
        private fb: FormBuilder,
        private dialogRef: MatDialogRef<GeoportalMapDialogComponent>,
        @Inject(MAT_DIALOG_DATA) data: any) {

        this.description = data.description;
        this.success = data.success;
        // this.create = data.create;
        // this.content = data.content;
        this.element = data.element;
        this.datasetId = data.datasetId;
        this.datasetName = data.datasetName;
        this.openGraph = data.openGraph;

        this.dataset = data.dataset;
        this.latlng = data.latlng;
        this.dateStart = data.dateStart;
        this.dateEnd = data.dateEnd;
        this.variable = data.variable;
        this.range = data.range;

        if(this.element) {
          this.form = this.fb.group({
            // cod: new FormControl(this.element.cod_algo_type),
            cod: new FormControl(null),
          })
        }
        else {
          this.form = this.fb.group({
            cod: new FormControl(null),
            // des: new FormControl(null),
            // ord: new FormControl(null)
          })
        }

    }
  ngAfterViewInit(): void {
  }

  ngOnInit() {
    if(!this.openGraph) {
      this.getMetadataTable();

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
    if(this.element) {
      // this.updateAlgoConfig();
    }
    else {
      // this.createAlgoConfig();
    }
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
    // console.log('METADATA TABLE =', response);
    // if(this.myDiv) {
    this.myDiv.nativeElement.innerHTML = response;

    // }
    // else {

    // this.graph.nativeElement.innerHTML = response;
    // }
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
    console.log('DATA =', data);
    console.log("TYPE IDMETA =", typeof this.datasetId);
    console.log("TYPE DIMENSIONS =", typeof this.dataset.dimensions);
    console.log("TYPE LAT =", typeof this.latlng.lat);
    console.log("TYPE LNG =", typeof this.latlng.lng);
    console.log("TYPE DATESTART =", typeof this.dateStart);
    console.log("TYPE DATEEND =", typeof this.dateEnd);
    console.log("TYPE VARIABLE =", typeof this.variable);
    console.log("TYPE RANGE =", typeof this.range);



    this.httpClient.post('http://localhost:8000/test/dataGraphTable', data, { responseType: 'text' }).subscribe(response => {
    console.log("GRAPH RESPONSE =", response);
    this.spinnerLoading = false;
    if(typeof response === 'string') {
      response = JSON.parse(response);
    }
    this.dataTable = response;
    console.log("LET'S WHAT WE GOT========",this.dataTable.data.table.rows);
    this.dataSource = new MatTableDataSource<any>(this.dataTable.data.table.rows);
    this.dataSource.paginator = this.paginator;

    // this.graph.nativeElement.innerHTML = response;

  });

  }

  // updateAlgoConfig() {
  //   this.httpService.post("adminAlgorithmConfiguration", {
  //     call: "editAlgoConfig",
  //     pkClient: this.element.cod_config,
  //     pkCodAlgoType: this.element.cod_algo_type,
  //     codAlgoType: this.form.get("cod")?.value,
  //     // des: this.form.get("des")?.value,
  //     // ord: this.form.get("ord")?.value
  //   }).subscribe({
  //     next: (res: any) => {
  //       console.log("OK =", res);
  //       this.dialogRef.close("ok");

  //     },
  //     error: (error: any) => {
  //       console.log("ERROR =", error);
  //       this.description = error.error;
  //       let obj = {
  //         id: "exists",
  //         desc: this.description
  //       };
  //       this.dialogRef.close(obj);
  //     }
  //   });
  // }

  // createAlgoConfig() {
  //   this.httpService.post("adminAlgorithmConfiguration", {
  //     call: "createAlgoConfig",
  //     codConfig: this.codConfig,
  //     codAlgoType: this.form.get("cod")?.value,
  //     // des: this.form.get("des")?.value,
  //     // ord: this.form.get("ord")?.value
  //   }).subscribe({
  //     next: (res: any) => {
  //       console.log("OK =", res);
  //       this.dialogRef.close("ok");

  //     },
  //     error: (error: any) => {
  //       console.log("ERROR =", error);
  //       this.description = error.error;
  //       let obj = {
  //         id: "exists",
  //         desc: this.description
  //       };
  //       this.dialogRef.close(obj);
  //     }
  //   });
  // }


}
