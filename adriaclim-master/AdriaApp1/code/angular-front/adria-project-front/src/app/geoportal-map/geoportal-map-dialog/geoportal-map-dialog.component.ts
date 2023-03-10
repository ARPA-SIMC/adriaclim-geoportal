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
  dataSource : any;

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
      // for(let key of this.dataTable.data.table.columnNames) {
        // if(key === "columnNames") {
            // const k = this.dataTable.data.table[key]
            console.log("KEY = ", key);
            // for(let attr in k) {
              // const a = k[attr];
              // key.forEach((a: any, ind: number) => {

                console.log("ATTR = ", key);
                // arr[ind] = {[a]: arr[ind]}
                console.log("ARR IND = ", arr[i]);
                // arr[a] = arr[ind];
                objArr[key] = arr[i];
                // arr1.push(objArr);
                // arr.splice(ind, 1);
                console.log("OBJ ARR = ", objArr);
                // arr =  {...arr};

                // console.log("ARR2 = ", arr);

                // arr[ind].forEach((arrInd: any) => {

                //   arr[ind][a] = arrInd;
                //   // console.log("ARR IND = ", arr[ind]);

                // });
                // arr[ind].map((el: any) => {
                //   // console.log("EL = ", el);

                //     arr[ind] = {[a]: el}
                //     console.log("ARR MAP = ", arr);

                // })
              // });
              // console.log("A = ", a);



        // console.log("ARR FOR = ", arr);

      // };

    })
    arr1.push(objArr);

  });
    this.dataTable.data.table.rows = [...arr1];
    // this.dataTable.data.table.rows.forEach((element: any) => {
      // });
    console.log("DATA TABLE = ", this.dataTable);
    if(this.dataTable.data.table.rows.length > 0) {
      this.dataSource = new MatTableDataSource(this.dataTable.data.table.rows);
      console.log("DATA SOURCE = ", this.dataSource);

      this.dataSource.paginator = this.paginator;
      console.log("DATA SOURCE PAGINATOR = ", this.dataSource.paginator);

    }


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
