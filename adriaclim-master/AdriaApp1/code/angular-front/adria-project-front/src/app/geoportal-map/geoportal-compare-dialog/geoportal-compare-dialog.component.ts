import { DatePipe } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Component, ElementRef, Inject, ViewChild, ChangeDetectorRef, AfterContentChecked, OnInit } from '@angular/core';
import { FormBuilder, FormControl, FormGroup, Validators } from '@angular/forms';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { Options, LabelType } from '@angular-slider/ngx-slider';
import { HttpService } from 'src/app/services/http.service';
import { ExtraParams } from 'src/app/interfaces/geoportal-compare-dialog-int';

@Component({
  selector: 'app-geoportal-compare-dialog',
  templateUrl: './geoportal-compare-dialog.component.html',
  styleUrls: ['./geoportal-compare-dialog.component.scss']
})
export class GeoportalCompareDialogComponent implements OnInit {
  activeLayersArray: any;
  form!: FormGroup;
  isIndicator!: boolean;
  firstDatasetVariables: any[] = [];
  secondDatasetVariables: any[] = [];
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

  valueOne: any = null;
  valueTwo: any = null;

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

    }

  async chargeAll() {
    try {
      this.getSelectedVarFirstDataset();
      this.getSelectedVarSecondDataset();

    }
    catch (error) {
      // reject(error);
      console.log("ERROR CHARGE ALL", error);

    }
  }

  /**
   * FUNZIONE CHE CONTROLLA SE IL NOME DEL METADATO DIMENSIONS E' UGUALE A UN DETERMINATO NOME E RITORNA IL NOME CORRETTO DA VISUALIZZARE
   */
  checkDimensions() {
    if(this.firstDataset.name.dimensions > 3) {

      let name = this.firstDataset.name.dimension_names.split(" ")[1];
      if (name === "depth") {
        // this.extraParam.name = "elevation";
        this.extraParamFirst = {
          name: "Elevation",
          minValue: - this.firstDataset.name.param_max,
          maxValue: - this.firstDataset.name.param_min,
          stepSize: Number(this.firstDataset.name.param_step),
          nameExtraParam: name,
        };

      }
      else {

        this.extraParamFirst = {
          name: 'Dim_' + name,
          minValue: this.firstDataset.name.param_min,
          maxValue: this.firstDataset.name.param_max,
          stepSize: Number(this.firstDataset.name.param_step),
          nameExtraParam: name,
        };

      }

    }

    if(this.secondDataset.name.dimensions > 3) {
      let name = this.secondDataset.name.dimension_names.split(" ")[1];

      if (name === "depth") {

        this.extraParamSecond = {
          name: "Elevation",
          minValue: - this.secondDataset.name.param_max,
          maxValue: - this.secondDataset.name.param_min,
          stepSize: Number(this.secondDataset.name.param_step),
          nameExtraParam: name,
        };

      }
      else{

        this.extraParamSecond = {
          name: 'Dim_' + name,
          minValue: this.secondDataset.name.param_min,
          maxValue: this.secondDataset.name.param_max,
          stepSize: Number(this.secondDataset.name.param_step),
          nameExtraParam: name,
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

  }

  close() {
      this.dialogRef.close("");
  }

  changeValueSliderOne(event: any) {
    this.valueOne = event.value;

  }

  changeValueSliderSecond(event: any) {
    this.valueTwo = event.value;

  }

  compareDatasets(){
    let data = {
      firstDataset: this.form.get('firstDataset')?.value,
      secondDataset: this.form.get('secondDataset')?.value,
      firstValue: this.checkForDepth1(),
      firstVarSel: this.form.get('variableFirstData')?.value,
      secondValue: this.checkForDepth2(),
      secondVarSel: this.form.get('variableSecondData')?.value,
    }
    this.dialogRef.close(data);

  }

  checkForDepth1() {
    if(!this.valueOne) {
      // se non è stato selezionato un valore prendi quello impostato di default
      return this.firstValue;
    }
    else{
      //dobbiamo controllare se è Elevation
      if(this.extraParamFirst.name === "Elevation"){
        return -this.valueOne;
      }
      else {
        return this.valueOne;
      }
    }

  }

  checkForDepth2() {
    if(!this.valueTwo) {
      // se non è stato selezionato un valore prendi quello impostato di default
      return this.secondValue;
    }
    else{
      //dobbiamo controllare se è Elevation
      if(this.extraParamSecond.name === "Elevation"){
        return -this.valueTwo;
      }
      else {
        return this.valueTwo;
      }
    }

  }

  /**
   * FUNZIONE CHE OTTIENE LE VARIABILI DEL PRIMO DATASET SELEZIONATO
   */
  async getSelectedVarFirstDataset(){

    this.firstDataset = this.form.get('firstDataset')?.value;
    // console.log("SELECTED VAR DATASET: ", this.firstDataset);

    if (this.firstDataset.name) {
      let variableNames = this.firstDataset.name.variable_names.split(" ");
      // let variableNames = first.name.variable_names.split(" ");
      let variableTypes = this.firstDataset.name.variable_types.split(" ");
      // console.log("VariableName===========",variableNames,"variable types==========",variableTypes);
      variableNames.forEach((vName:any, index: number) =>{
     // Include variables that are not "time", "latitude", or "longitude" and have a type of "float"
      if (
        vName !== "time" && vName !== "latitude" && vName !== "longitude" &&
        (variableTypes[index] === "float" || variableTypes[index] === "double")
      ) {
        // console.log("VNAME===========", vName, "variable types==========", variableTypes[index]);

        this.firstDatasetVariables.push({ name: vName, type: variableTypes[index] });
      }
      });
    }
    else if (this.firstDataset.variable_names) {
      //sono tabledap
      // this.firstDatasetVariables = this.firstDataset.variable_names.split(" ");
      let variableNames = this.firstDataset.variable_names.split(" ");
      // let variableNames = first.name.variable_names.split(" ");
      let variableTypes = this.firstDataset.variable_types.split(" ");
      // console.log("VariableName===========",variableNames,"variable types==========",variableTypes);
      variableNames.forEach((variableName:any, index: number) =>{
     // Include variables that are not "time", "latitude", or "longitude" and have a type of "float"
      if (
        variableName !== "time" && variableName !== "latitude" && variableName !== "longitude" &&
        (variableTypes[index] === "float" || variableTypes[index] === "double")
      ) {
        this.firstDatasetVariables.push({ name: variableName, type: variableTypes[index] });
      }
      });
    }

    this.form.get("variableFirstData")?.setValue(this.firstDatasetVariables[this.firstDatasetVariables.length - 1]["name"]);

  }

  /**
   * FUNZIONE CHE OTTIENE LE VARIABILI DEL SECONDO DATASET SELEZIONATO
   */
  async getSelectedVarSecondDataset(){

    // await this.chargeAll();
    // setTimeout(() => {
    //   this.checkDimensions();

    // }, 500);
    this.secondDataset = this.form.get('secondDataset')?.value;

    if (this.secondDataset.name) {
      let variableNames = this.secondDataset.name.variable_names.split(" ");
      // let variableNames = first.name.variable_names.split(" ");
      let variableTypes = this.secondDataset.name.variable_types.split(" ");
      // console.log("VariableName===========",variableNames,"variable types==========",variableTypes);
      variableNames.forEach((variableName:any, index: number) =>{
     // Include variables that are not "time", "latitude", or "longitude" and have a type of "float"
      if (
        variableName !== "time" && variableName !== "latitude" && variableName !== "longitude" &&
        (variableTypes[index] === "float" || variableTypes[index] === "double")
      ) {
        this.secondDatasetVariables.push({ name: variableName, type: variableTypes[index] });
      }
      });
    }
    else if (this.secondDataset.variable_names) {
      //sono tabledap
      // this.firstDatasetVariables = this.firstDataset.variable_names.split(" ");
      let variableNames = this.secondDataset.variable_names.split(" ");
      // let variableNames = first.name.variable_names.split(" ");
      let variableTypes = this.secondDataset.variable_types.split(" ");
      // console.log("VariableName===========",variableNames,"variable types==========",variableTypes);
      variableNames.forEach((variableName:any, index: number) =>{
     // Include variables that are not "time", "latitude", or "longitude" and have a type of "float"
      if (
        variableName !== "time" && variableName !== "latitude" && variableName !== "longitude" &&
        (variableTypes[index] === "float" || variableTypes[index] === "double")
      ) {
        this.secondDatasetVariables.push({ name: variableName, type: variableTypes[index] });
      }
      });
    }

    this.form.get("variableSecondData")?.setValue(this.secondDatasetVariables[this.secondDatasetVariables.length - 1]["name"]);

  }

}
