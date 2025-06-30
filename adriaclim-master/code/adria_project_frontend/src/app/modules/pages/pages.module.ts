import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { PagesRoutingModule } from './pages-routing.module';
import { PagesComponent } from './pages.component';
import { WelcomeComponent } from './welcome/welcome.component';
import { AngularMatModule } from '../services/angular-mat/angular-mat.module';


@NgModule({
  declarations: [
    PagesComponent,
    WelcomeComponent
  ],
  imports: [
    CommonModule,
    PagesRoutingModule,
    // Modulo che comprende tutti i moduli di angular material
    AngularMatModule,
  ],
  exports: [
    WelcomeComponent
  ]
})
export class PagesModule { }
