import { DatePipe } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { AfterViewInit, Component, ElementRef, Inject, ViewChild, ChangeDetectorRef, AfterContentChecked, OnInit } from '@angular/core';
import { FormBuilder, FormControl, FormGroup, Validators } from '@angular/forms';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { Observable } from 'rxjs';
// import * as saveAs from 'file-saver';
import { saveAs } from 'file-saver';
import { Options, LabelType } from '@angular-slider/ngx-slider';
import { HttpService } from 'src/app/services/http.service';
import { MAT_SELECT_CONFIG } from '@angular/material/select';
import { last } from 'lodash';

@Component({
  selector: 'app-geoportal-compare-dialog',
  templateUrl: './geoportal-compare-dialog.component.html',
  styleUrls: ['./geoportal-compare-dialog.component.scss']
})
export class GeoportalCompareDialogComponent implements OnInit, AfterViewInit, AfterContentChecked {
  activeLayersArray: any;
  form!: FormGroup;
  isIndicator!: boolean;
  firstDatasetVariables: any;
  secondDatasetVariables: any;
  compareObj: any;

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
    }
  ngOnInit(): void {
    this.getSelectedVarFirstDataset();
    this.getSelectedVarSecondDataset();
    console.log("FIRST DATASET", this.form.get('firstDataset')?.value);
    console.log("SECOND DATASET", this.form.get('secondDataset')?.value);
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

  getSelectedVarFirstDataset(){
    let firstDataset = this.form.get('firstDataset')?.value;

    if (firstDataset.name) {
      this.firstDatasetVariables = firstDataset.name.variable_names.split(" ");
    }
    else if (firstDataset.name.variable_names) {
      this.firstDatasetVariables = firstDataset.variable_names.split(" ");
    }
    this.isIndicator = firstDataset.name.griddap_url !== "" ? false : true;
    if (this.isIndicator) {
      this.firstDatasetVariables = this.firstDatasetVariables.slice(-1);
    }


    this.form.get("variableFirstData")?.setValue(this.firstDatasetVariables[this.firstDatasetVariables.length - 1]);


  }

  getSelectedVarSecondDataset(){
    let secondDataset = this.form.get('secondDataset')?.value;

    if (secondDataset.name) {
      this.secondDatasetVariables = secondDataset.name.variable_names.split(" ");
    }
    else if (secondDataset.name.variable_names) {
      this.secondDatasetVariables = secondDataset.variable_names.split(" ");
    }
    this.isIndicator = secondDataset.name.griddap_url !== "" ? false : true;
    if (this.isIndicator) {
      this.secondDatasetVariables = this.secondDatasetVariables.slice(-1);
    }

    this.form.get("variableSecondData")?.setValue(this.secondDatasetVariables[this.secondDatasetVariables.length - 1]);

  }



  ngAfterContentChecked(): void {
      this.changeDetector.detectChanges();
    }

  ngAfterViewInit(): void {
  }
}
