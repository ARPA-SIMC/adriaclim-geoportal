import { HttpClient } from '@angular/common/http';
import { Component, ElementRef, Inject, ViewChild } from '@angular/core';
import { FormBuilder, FormControl, FormGroup } from '@angular/forms';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';

@Component({
  selector: 'app-geoportal-map-dialog',
  templateUrl: './geoportal-map-dialog.component.html',
  styleUrls: ['./geoportal-map-dialog.component.scss']
})
export class GeoportalMapDialogComponent {

  form!: FormGroup;
  description:string;
  // create: boolean;
  success: boolean;
  // content = {};
  element: any;
  datasetId: string;
  datasetName: string;

  algoType: any;
  @ViewChild('metadataTable') myDiv!: ElementRef;

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

    ngOnInit() {

      this.getMetadataTable();
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
    //   this.httpClient.post('http://localhost:8000/test/metadataTable', {
    //   idMeta: this.datasetId
    // }).subscribe({
    //   next: (res: any) => {
    //     console.log('METADATA TABLE =', res);
    //     // this.metadata = res;
    //     // this.getLayers(idMeta);
    //   },
    //   error: (msg: any) => {
    //     console.log('METADATA ERROR: ', msg);
    //   }

    // });

    let data = {
      idMeta: this.datasetId
    }
    this.httpClient.post('http://localhost:8000/test/metadataTable', data, { responseType: 'text' }).subscribe(response => {
      console.log('METADATA TABLE =', response);
      this.myDiv.nativeElement.innerHTML = response;
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
