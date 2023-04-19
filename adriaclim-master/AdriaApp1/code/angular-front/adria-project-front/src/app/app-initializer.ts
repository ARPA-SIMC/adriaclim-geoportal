import { Injectable } from '@angular/core';
import { AppComponent } from './app.component';
import { initializeApp } from './app.component';

@Injectable()
export class AppInitializer {
  constructor(private appComponent: AppComponent) {}

  initialize() {
    // Your initialization code goes here
    initializeApp(this.appComponent)();
  }
}