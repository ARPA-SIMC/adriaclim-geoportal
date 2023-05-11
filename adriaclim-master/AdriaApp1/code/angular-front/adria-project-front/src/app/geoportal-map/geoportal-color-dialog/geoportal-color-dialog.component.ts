import { DatePipe } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { AfterViewInit, Component, ElementRef, Inject, ViewChild, ChangeDetectorRef, AfterContentChecked } from '@angular/core';
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
  selector: 'app-geoportal-color-dialog',
  templateUrl: './geoportal-color-dialog.component.html',
  styleUrls: ['./geoportal-color-dialog.component.scss']
})
export class GeoportalColorDialogComponent implements AfterViewInit, AfterContentChecked {
  description: string;
  success: boolean;
  datasetName: any;
  openGraph: any;
  // valueMinColor: any = "#f44336";
  valueMinColor: any;
  valueMinMidColor: any;
  valueMidMaxColor: any;
  valueMidColor: any;
  valueMaxColor: any;
  // valueMidColor: any = "#9c27b0";
  // valueMaxColor: any = "#3f51b5";
  form!: FormGroup;

  constructor(
    private changeDetector: ChangeDetectorRef,
    private httpService: HttpService,
    public datePipe: DatePipe,
    private httpClient: HttpClient,
    private fb: FormBuilder,
    private dialogRef: MatDialogRef<GeoportalColorDialogComponent>,
    @Inject(MAT_DIALOG_DATA) data: any){
      this.description = data.description;
      this.success = data.success;
      this.datasetName = data.datasetName;
      this.openGraph = data.openGraph;
      this.valueMaxColor = data.valueMaxColor;
      this.valueMinColor = data.valueMinColor;
      this.valueMidColor = data.valueMidColor;
      this.valueMinMidColor = data.valueMinMidColor;
      this.valueMidMaxColor = data.valueMidMaxColor;
      // this.valueMaxMidColor = this.mixColors(this.valueMidColor, this.valueMaxColor);
      // this.valueMinMidColor = this.mixColors(this.valueMinColor,this.valueMidColor);
      this.form = this.fb.group({
        minColor: new FormControl(this.valueMinColor),
        midColor: new FormControl(this.valueMidColor),
        maxColor: new FormControl(this.valueMaxColor),
        // minMidColor: new FormControl(this.mixColors(this.valueMinColor,this.valueMidColor)),
        // midMaxColor: new FormControl(this.mixColors(this.valueMidColor, this.valueMaxColor)),
        minMidColor: new FormControl(this.valueMinMidColor),
        midMaxColor: new FormControl(this.valueMidMaxColor),
      })
      let colorStorage = localStorage.getItem(this.datasetName);
      // let colorStorage: any;
      // for (let i = 0; i < localStorage.length; i++) {
      //   let key: any = localStorage.key(i);
      //   let value: any = localStorage.getItem(key);
      //   console.log("CHIAVE =", key,"VALORE =", value);
      //   if(key === this.datasetName){
      //     colorStorage = localStorage.getItem(key);
      //     let colorStorageJson = JSON.parse(colorStorage);
      //     this.form.get('minColor')?.setValue(colorStorageJson.minColor);
      //     this.form.get('midColor')?.setValue(colorStorageJson.midColor);
      //     this.form.get('maxColor')?.setValue(colorStorageJson.maxColor);
      //     this.form.get('minMidColor')?.setValue(colorStorageJson.minMidColor);
      //     this.form.get('midMaxColor')?.setValue(colorStorageJson.midMaxColor);
      //   }
      // };
      if(colorStorage) {
        let colorStorageJson = JSON.parse(colorStorage);
        this.form.get('minColor')?.setValue(colorStorageJson.minColor);
        this.form.get('midColor')?.setValue(colorStorageJson.midColor);
        this.form.get('maxColor')?.setValue(colorStorageJson.maxColor);
        this.form.get('minMidColor')?.setValue(colorStorageJson.minMidColor);
        this.form.get('midMaxColor')?.setValue(colorStorageJson.midMaxColor);
      }
    // nel caso di local storage
      // if(colorStorage){
        //è memorizzato nella cache
        // this.valueMinColor = colorStorageJson.valueMinColor;
        // this.valueMinMidColor = colorStorageJson.valueMinMidColor;
        // this.valueMidColor = colorStorageJson.valueMidColor;
        // this.valueMidMaxColor = colorStorageJson.valueMidMaxColor;
        // this.valueMaxColor = colorStorageJson.valueMaxColor;


      // }
      // else {

      // }
    }

  close() {
      this.dialogRef.close("");
  }

  restoreDefault(){
    this.dialogRef.close("restoreDefault");
  }

  updateColors(){


    this.valueMinColor =  this.form.get('minColor')?.value;
    this.valueMaxColor = this.form.get('maxColor')?.value;
    this.valueMidColor = this.form.get('midColor')?.value;
    this.valueMidMaxColor = this.mixColors(this.valueMidColor, this.valueMaxColor);
    this.valueMinMidColor = this.mixColors(this.valueMinColor,this.valueMidColor);
    console.log("this.valueMaxMidColor",this.valueMidMaxColor);
    console.log("this.valueMinMidColor",this.valueMinMidColor);
    this.form.get('minMidColor')?.setValue(this.valueMinMidColor);
    this.form.get('midMaxColor')?.setValue(this.valueMidMaxColor);

    try{
      localStorage.setItem(this.datasetName,JSON.stringify(this.form.value));
    }catch(error:any){
      if(error instanceof DOMException && error.name === 'QuotaExceededError'){
        //localstorage è pieno
        let firstKey = localStorage.key(0);
        if(firstKey) {
          localStorage.removeItem(firstKey);
          localStorage.setItem(this.datasetName,JSON.stringify(this.form.value));
        }

      }

    }
    // console.log("LOCAL STORAGE =", localStorage.getItem(this.datasetName));

    //i colori nuovi ci sono, ora bisogna aggiornare la legenda e la mappa
    //step 1: aggiornare la legenda
    this.dialogRef.close(this.form.value);

    //step 2: aggiornare la mappa
    // this.close();
  }

  mixColors(color1: string, color2: string): string {
    // Convert hexadecimal color strings to RGB values
    const rgb1 = this.hexToRgb(color1);
    const rgb2 = this.hexToRgb(color2);

    // Mix the RGB values
    const mixedRgb = this.mixRgb(rgb1, rgb2, 0.5);

    // Convert the mixed RGB values back to hexadecimal color string
    const mixedColor = this.rgbToHex(mixedRgb.r, mixedRgb.g, mixedRgb.b);

    return mixedColor;
  }

  hexToRgb(hex: string): { r: number; g: number; b: number } {
    // Remove the # symbol from the hexadecimal color string
    hex = hex.replace("#", "");

    // Split the string into RGB components
    const r = parseInt(hex.substring(0, 2), 16);
    const g = parseInt(hex.substring(2, 4), 16);
    const b = parseInt(hex.substring(4, 6), 16);

    return { r, g, b };
  }

  rgbToHex(r: number, g: number, b: number): string {
    // Convert the RGB values to hexadecimal strings and concatenate them
    const hexR = r.toString(16).padStart(2, "0");
    const hexG = g.toString(16).padStart(2, "0");
    const hexB = b.toString(16).padStart(2, "0");

    return `#${hexR}${hexG}${hexB}`;
  }

  mixRgb(rgb1: { r: number; g: number; b: number }, rgb2: { r: number; g: number; b: number }, ratio: number): { r: number; g: number; b: number } {
    // Mix the RGB values based on the given ratio
    const mixedR = Math.round(rgb1.r * (1 - ratio) + rgb2.r * ratio);
    const mixedG = Math.round(rgb1.g * (1 - ratio) + rgb2.g * ratio);
    const mixedB = Math.round(rgb1.b * (1 - ratio) + rgb2.b * ratio);

    return { r: mixedR, g: mixedG, b: mixedB };
  }




  ngAfterContentChecked(): void {
      this.changeDetector.detectChanges();
    }

  ngAfterViewInit(): void {
  }
}
