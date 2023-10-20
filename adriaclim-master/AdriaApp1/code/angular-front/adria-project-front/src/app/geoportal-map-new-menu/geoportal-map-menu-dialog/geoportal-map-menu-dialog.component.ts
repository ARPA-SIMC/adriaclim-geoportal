import { DatePipe } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Component, ElementRef, Inject, ViewChild, ChangeDetectorRef, AfterContentChecked, OnInit } from '@angular/core';
import { FormBuilder, FormControl, FormGroup, Validators } from '@angular/forms';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { Options, LabelType } from '@angular-slider/ngx-slider';
import { HttpService } from 'src/app/services/http.service';
import { ExtraParams } from 'src/app/interfaces/geoportal-compare-dialog-int';

@Component({
  selector: 'app-geoportal-map-menu-dialog',
  templateUrl: './geoportal-map-menu-dialog.component.html',
  styleUrls: ['./geoportal-map-menu-dialog.component.scss']
})
export class GeoportalMapMenuDialogComponent {

  activeLayersArray: any;
  form!: FormGroup;
  isIndicator!: boolean;
  firstDatasetVariables: any[] = [];
  secondDatasetVariables: any[] = [];
  compareObj: any;

  firstValue: any = 100;
  secondValue: any = 100;


  // Nuove
  categoryDatasets: any;
  scaleDatasets: any;
  timeperiodDatasets: any;
  menuDatasets: any;
  resAllNodes: any;

  searchFilter: any;

  constructor(
    private changeDetector: ChangeDetectorRef,
    private httpService: HttpService,
    public datePipe: DatePipe,
    private httpClient: HttpClient,
    private fb: FormBuilder,
    private dialogRef: MatDialogRef<GeoportalMapMenuDialogComponent>,
    @Inject(MAT_DIALOG_DATA) data: any){
      // this.activeLayersArray = data.activeLayersArray;
      // this.categoryDatasets = data.categoryDatasets,
      // this.scaleDatasets = data.scaleDatasets,
      // this.timeperiodDatasets = data.timeperiodDatasets,
      // this.menuDatasets = data.menuDatasets,
      this.compareObj = data.compareObj;
      this.form = this.fb.group({
        category: new FormControl(),
        scale: new FormControl(),
        timeperiod: new FormControl(),
        menu: new FormControl(),
      });

      this.getAllNodes();

    }


  async ngOnInit() {

    // this.chargeAll()
    // setTimeout(() => {
    // this.checkDimensions();

    // }, 500);

  }

  close() {
      this.dialogRef.close("");
  }

  ok(){
    // let data = {
    //   firstDataset: this.form.get('firstDataset')?.value,
    //   secondDataset: this.form.get('secondDataset')?.value,
    //   firstVarSel: this.form.get('variableFirstData')?.value,
    //   secondVarSel: this.form.get('variableSecondData')?.value,
    // }
    // this.dialogRef.close(data);

    this.dialogRef.close("ok");

  }

  /**
   * FUNZIONE CHE RICHIAMA TUTTI I NUOVI DATASET DI ERDDAP ATTRAVERSO I SERVIZI API COLLEGATI AI NODI DEL DATABASE
   */
  getAllNodes() {
    this.categoryDatasets = [];

    let tmpCategoryDatasets: any[] = [];
    let tmpScale: any[] = [];
    let tmpTimeperiods: any[] = [];

    this.httpService.post('test/allNodes', {
    }).subscribe({
      next: (res: any) => {
        // console.log("SUB NEXT");
        console.log("RES NODES =", res.nodes);

        this.resAllNodes = res.nodes;

        this.resAllNodes.forEach((element: any) => {
          if(element.adriaclim_dataset !== "no" && element.adriaclim_dataset !== "No" && element.adriaclim_dataset !== "Indicator") {
            tmpCategoryDatasets.push(element.adriaclim_dataset);
          }
        });
        this.categoryDatasets = [...new Set(tmpCategoryDatasets)];
        this.form.get("category")?.setValue(this.categoryDatasets[0]);

        this.resAllNodes.forEach((el: any) => {
          if(el.adriaclim_dataset === this.form.get("category")?.value) {
            tmpScale.push(el.adriaclim_scale);
          }
        });
        this.scaleDatasets = [...new Set(tmpScale)];
        this.form.get("scale")?.setValue(this.scaleDatasets[0]);

        this.resAllNodes.forEach((el: any) => {
          if (el.adriaclim_dataset === this.form.get("category")?.value && el.adriaclim_scale === this.form.get("scale")?.value) {
            tmpTimeperiods.push(el.adriaclim_timeperiod);
          }
        });
        this.timeperiodDatasets = [...new Set(tmpTimeperiods)];
        this.form.get("timeperiod")?.setValue(this.timeperiodDatasets[0]);

        this.menuDatasets = this.resAllNodes.filter((el: any) => el.adriaclim_dataset === this.form.get("category")?.value && el.adriaclim_scale === this.form.get("scale")?.value && el.adriaclim_timeperiod === this.form.get("timeperiod")?.value);

        console.log("CATEGORY DATASETS =", this.categoryDatasets);
        console.log("SCALE DATASETS =", this.scaleDatasets);
        console.log("TIMEPERIOD DATASETS =", this.timeperiodDatasets);
        console.log("MENU DATASETS =", this.menuDatasets);
        console.log("FORM MENU DATASETS =", this.form.value);

        this.searchFilter = this.menuDatasets;

      },
      error: (msg: any) => {
        console.log("SUB ERROR");

        console.log('ALL NODES ERROR: ', msg);
      }
    })
    // this.dataSource.data = TREE_DATA;

  }

  /**
   * Funzione che cambia dinamicamente gli elementi all'interno dei vari menu
   */
  changeSel(type?: string) {

    let tmpScale: any[] = [];
    let tmpTimeperiods: any[] = [];

    if(type === "c") {

      this.resAllNodes.forEach((el: any) => {
        if(el.adriaclim_dataset === this.form.get("category")?.value) {
          tmpScale.push(el.adriaclim_scale);
        }
      });
      this.scaleDatasets = [...new Set(tmpScale)];
      this.form.get("scale")?.setValue(this.scaleDatasets[0]);

      this.resAllNodes.forEach((el: any) => {
        if (el.adriaclim_dataset === this.form.get("category")?.value && el.adriaclim_scale === this.form.get("scale")?.value) {
          tmpTimeperiods.push(el.adriaclim_timeperiod);
        }
      });
      this.timeperiodDatasets = [...new Set(tmpTimeperiods)];
      this.form.get("timeperiod")?.setValue(this.timeperiodDatasets[0]);

      this.menuDatasets = this.resAllNodes.filter((el: any) => el.adriaclim_dataset === this.form.get("category")?.value && el.adriaclim_scale === this.form.get("scale")?.value && el.adriaclim_timeperiod === this.form.get("timeperiod")?.value);

    }
    else if(type === "s") {
      this.resAllNodes.forEach((el: any) => {
        if (el.adriaclim_dataset === this.form.get("category")?.value && el.adriaclim_scale === this.form.get("scale")?.value) {
          tmpTimeperiods.push(el.adriaclim_timeperiod);
        }
      });
      this.timeperiodDatasets = [...new Set(tmpTimeperiods)];
      this.form.get("timeperiod")?.setValue(this.timeperiodDatasets[0]);

    }
    else if(type === "t") {
      this.menuDatasets = this.resAllNodes.filter((el: any) => el.adriaclim_dataset === this.form.get("category")?.value && el.adriaclim_scale === this.form.get("scale")?.value && el.adriaclim_timeperiod === this.form.get("timeperiod")?.value);

    }

    this.searchFilter = this.menuDatasets;
  }

  onKey(event: any) {
    console.log("EVENT =", event.target.value);

    this.searchFilter = this.search(event.target.value);
    }

  search(value: string) {
    if(value) {
      let filter = value.toLowerCase();

      let menuFiltered = this.menuDatasets.filter((option: any) => option.title.toLowerCase().includes(filter));

      return menuFiltered;

    }
    else {
      return this.menuDatasets;
    }
  }



}
