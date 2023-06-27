import { DatePipe } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { AfterViewInit, Component, ElementRef, Inject, ViewChild, ChangeDetectorRef, AfterContentChecked, OnInit } from '@angular/core';
import { FormBuilder, FormControl, FormGroup, Validators } from '@angular/forms';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { Observable, async } from 'rxjs';
// import * as saveAs from 'file-saver';
import { saveAs } from 'file-saver';
import { Options, LabelType } from '@angular-slider/ngx-slider';
import { HttpService } from 'src/app/services/http.service';
import { MAT_SELECT_CONFIG } from '@angular/material/select';
import { last } from 'lodash';


interface ExtraParams {
  name: string;
  nameExtraParam: string;
  minValue: number;
  maxValue: number;
  stepSize: number;
}
@Component({
  selector: 'app-geoportal-compare-dialog',
  templateUrl: './geoportal-compare-dialog.component.html',
  styleUrls: ['./geoportal-compare-dialog.component.scss']
})
export class GeoportalCompareDialogComponent implements OnInit, AfterViewInit {
  activeLayersArray: any;
  form!: FormGroup;
  isIndicator!: boolean;
  firstDatasetVariables: any;
  secondDatasetVariables: any;
  compareObj: any;

  firstOptions: Options = {
    floor: 0,
    ceil: 100,
    step: 1,
  };

  secondOptions: Options = {
    floor: 0,
    ceil: 100,
    step: 1,
  };

  firstValue: any = 100;
  secondValue: any = 100;

  extraParamFirst: ExtraParams = {
    name: "Elevation",
    minValue: 0,
    maxValue: 0,
    stepSize: 0,
    nameExtraParam: "ExtraElevation",
  };
  extraParamSecond: ExtraParams = {
    name: "Elevation",
    minValue: 0,
    maxValue: 0,
    stepSize: 0,
    nameExtraParam: "ExtraElevation",
  };

  firstDataset: any;
  secondDataset: any;
  sliderForm!: FormGroup;

  constructor(
    private changeDetector: ChangeDetectorRef,
    private httpService: HttpService,
    public datePipe: DatePipe,
    private httpClient: HttpClient,
    private fb: FormBuilder,
    private dialogRef: MatDialogRef<GeoportalCompareDialogComponent>,
    @Inject(MAT_DIALOG_DATA) data: any){
      this.activeLayersArray = data.activeLayersArray;
      this.compareObj = data.compareObj;
      this.form = this.fb.group({
        firstDataset: new FormControl(this.activeLayersArray[this.activeLayersArray.length - 1]),
        secondDataset: new FormControl(this.activeLayersArray[this.activeLayersArray.length - 2]),
        variableFirstData: new FormControl(),
        variableSecondData: new FormControl(),
      });
      this.sliderForm = this.fb.group({
        firstSlider: new FormControl(this.firstValue),
      });
      // this.firstOptions = {
      //   floor: this.form.get('firstDataset')?.value.name.param_min,
      //   ceil: this.form.get('firstDataset')?.value.name.param_max,
      //   step: Number(this.form.get('firstDataset')?.value.name.param_step.toFixed(4)),
      // };

      // this.secondOptions = {
      //   floor: this.form.get('secondDataset')?.value.name.param_min,
      //   ceil: this.form.get('secondDataset')?.value.name.param_max,
      //   step: Number(this.form.get('secondDataset')?.value.name.param_step.toFixed(4)),
      // };

    }

  async chargeAll() {
    // return new Promise<any>((resolve, reject) => {
    try {
      this.getSelectedVarFirstDataset();
      this.getSelectedVarSecondDataset();
      console.log("FIRST DATASET", this.form.get('firstDataset')?.value);
      console.log("SECOND DATASET", this.form.get('secondDataset')?.value);
      // resolve({
      //   firstDataset: this.firstDataset,
      //   secondDataset: this.secondDataset
      // }

      // );

    }
    catch (error) {
      // reject(error);
      console.log("ERROR CHARGE ALL", error);

    }
    // this.changeDetector.detectChanges();

    // });
  }

  checkDimensions() {
    if(this.firstDataset.name.dimensions > 3) {
      console.log("PARAM MAX TYPEOF", typeof this.firstDataset.name.param_max);

      console.log("TYPE OF FIRST VALUE", typeof this.firstValue);

      let name = this.firstDataset.name.dimension_names.split(" ")[1];
      console.log("NAME PARAM AGGIUNTIVO FIRST DATASET======",name);
      if (name === "depth") {
        // this.extraParam.name = "elevation";
        this.extraParamFirst = {
          name: "Elevation",
          minValue: - this.firstDataset.name.param_max,
          maxValue: - this.firstDataset.name.param_min,
          stepSize: Number(this.firstDataset.name.param_step),
          nameExtraParam: name,
        };


        // this.extraParamExport = {
        //   name: "Depth",
        //   minValue: min,
        //   maxValue: max,
        //   stepSize: step,
        //   nameExtraParam: name,
        // }

        // this.firstOptions = {
        //   floor: - this.firstDataset.name.param_max,
        //   ceil: - this.firstDataset.name.param_min,
        //   step: Number(this.firstDataset.name.param_step.toFixed(4)),
        // };

      }
      else {

        this.firstOptions = {
          floor: this.firstDataset.name.param_min,
          ceil: this.firstDataset.name.param_max,
          step: Number(this.firstDataset.name.param_step.toFixed(4)),
        };

        // this.extraParamExport = {
        //   name: "Dim_" + name,
        //   minValue: min,
        //   maxValue: max,
        //   stepSize: step,
        //   nameExtraParam: name,
        // }
      }


    }

    if(this.secondDataset.name.dimensions > 3) {
      let name = this.secondDataset.name.dimension_names.split(" ")[1];
      console.log("NAME PARAM AGGIUNTIVO SECOND DATASET======",name);

      if (name === "depth") {


        this.extraParamSecond = {
          name: "Elevation",
          minValue: - this.firstDataset.name.param_max,
          maxValue: - this.firstDataset.name.param_min,
          stepSize: Number(this.firstDataset.name.param_step),
          nameExtraParam: name,
        };

        // this.secondOptions = {
        //   floor: this.secondDataset.name.param_min,
        //   ceil: this.secondDataset.name.param_max,
        //   step: Number(this.secondDataset.name.param_step.toFixed(4)),
        // };

      }
      else{

        this.secondOptions = {
          floor: - this.secondDataset.name.param_max,
          ceil: - this.secondDataset.name.param_min,
          step: Number(this.secondDataset.name.param_step.toFixed(4)),
        };
      }
    }
    this.firstValue = this.firstDataset.name.param_max.toFixed(4);
    this.secondValue = this.secondDataset.name.param_max.toFixed(4);

    this.firstOptions = {
      floor: this.extraParamFirst.minValue,
      ceil: this.extraParamFirst.maxValue,
      step: Number(this.extraParamFirst.stepSize.toFixed(4)),
    };

    this.secondOptions = {
      floor: this.extraParamSecond.minValue,
      ceil: this.extraParamSecond.maxValue,
      step: Number(this.extraParamSecond.stepSize.toFixed(4)),
    };

    this.changeDetector.detectChanges();

  }

  async ngOnInit() {
    this.chargeAll()
    setTimeout(() => {
    this.checkDimensions();

    }, 500);
    // setTimeout(() => {

    // }, 500);


  }

  close() {
      this.dialogRef.close("");
  }

  compareDatasets(){
    let data = {
      firstDataset: this.form.get('firstDataset')?.value,
      secondDataset: this.form.get('secondDataset')?.value,
      firstVarSel: this.form.get('variableFirstData')?.value,
      secondVarSel: this.form.get('variableSecondData')?.value,
    }
    this.dialogRef.close(data);

    // console.log("FIRST DATASET: ", this.form.get('firstDataset')?.value);
    // console.log("SECOND DATASET: ", this.form.get('secondDataset')?.value);
    // console.log("FIRST VAR: ", this.form.get('variableFirstData')?.value);
    // console.log("SECOND VAR: ", this.form.get('variableSecondData')?.value);

  }

  async getSelectedVarFirstDataset(){
    // this.firstDataset = this.form.get('firstDataset')?.value;
    // this.chargeAll();
    // setTimeout(() => {
    //   this.checkDimensions();
    this.firstDataset = this.form.get('firstDataset')?.value;

    // }, 500);
    // let firstDataset = this.form.get('firstDataset')?.value;

    if (this.firstDataset.name) {
      this.firstDatasetVariables = this.firstDataset.name.variable_names.split(" ");
    }
    else if (this.firstDataset.name.variable_names) {
      this.firstDatasetVariables = this.firstDataset.variable_names.split(" ");
    }
    this.isIndicator = this.firstDataset.name.griddap_url !== "" ? false : true;
    if (this.isIndicator) {
      this.firstDatasetVariables = this.firstDatasetVariables.slice(-1);
    }


    this.form.get("variableFirstData")?.setValue(this.firstDatasetVariables[this.firstDatasetVariables.length - 1]);

    // this.options = {
    //   floor: firstDataset.name.param_min,
    //   ceil: firstDataset.name.param_max,
    //   step: Number(this.extraParam.stepSize.toFixed(4)),
    // };


  }

  async getSelectedVarSecondDataset(){
    // await this.chargeAll();
    // setTimeout(() => {
    //   this.checkDimensions();

    // }, 500);
    this.secondDataset = this.form.get('secondDataset')?.value;

    // let secondDataset = this.form.get('secondDataset')?.value;

    if (this.secondDataset.name) {
      this.secondDatasetVariables = this.secondDataset.name.variable_names.split(" ");
    }
    else if (this.secondDataset.name.variable_names) {
      this.secondDatasetVariables = this.secondDataset.variable_names.split(" ");
    }
    this.isIndicator = this.secondDataset.name.griddap_url !== "" ? false : true;
    if (this.isIndicator) {
      this.secondDatasetVariables = this.secondDatasetVariables.slice(-1);
    }

    this.form.get("variableSecondData")?.setValue(this.secondDatasetVariables[this.secondDatasetVariables.length - 1]);

  }



  // ngAfterContentChecked(): void {
  //     this.changeDetector.detectChanges();
  //   }

  ngAfterViewInit(): void {


  }

  // sliderControl(event: any) {
  //   // console.log("EVENTO SLIDERRRRRRRRR =", event.value);
  //   this.valueCustom = event.value;
  //   let metaId: any;
  //   if (this.selData.get("dataSetSel")?.value.name.dataset_id) {
  //     metaId = this.selData.get("dataSetSel")?.value.name.dataset_id;
  //   }
  //   else if (this.selData.get("dataSetSel")?.value.name.id) {
  //     metaId = this.selData.get("dataSetSel")?.value.name.id;
  //   }
  //   this.getMeta(metaId, "ok", this.valueCustom);
  // }



}
