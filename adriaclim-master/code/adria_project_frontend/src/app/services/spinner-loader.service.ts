import { Injectable } from '@angular/core';
import { Subject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class SpinnerLoaderService {

  spinnerShow: boolean = false;
  // spinnerShow: Subject<boolean> = new Subject<boolean>();

  constructor() {
    // this.spinnerShow.next(false);
  }

  // getSpinnerShow() {
  //   return this.spinnerShow;
  // }

  // setSpinnerShow(value: boolean) {
  //   this.spinnerShow.next(value);
  // }
}
