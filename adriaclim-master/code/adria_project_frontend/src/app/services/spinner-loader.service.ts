import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class SpinnerLoaderService {

  spinnerShow = false;
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
