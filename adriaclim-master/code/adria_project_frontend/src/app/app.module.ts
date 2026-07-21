import { NgModule, LOCALE_ID } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { HttpClientModule } from '@angular/common/http';
import { GeoportalMapComponent } from './geoportal-map/geoportal-map.component';
import { FlexLayoutModule } from '@angular/flex-layout';
import { MatMenuTrigger } from '@angular/material/menu';
import { OverlayModule } from '@angular/cdk/overlay';
import { ReactiveFormsModule } from '@angular/forms';
import {MAT_DATE_LOCALE} from '@angular/material/core';

import {CdkListboxModule} from '@angular/cdk/listbox';
import {PortalModule} from '@angular/cdk/portal';
import {ScrollingModule} from '@angular/cdk/scrolling';
import {CdkTreeModule} from '@angular/cdk/tree';
import {CdkMenuModule} from '@angular/cdk/menu';
import { GeoportalMapDialogComponent } from './geoportal-map/geoportal-map-dialog/geoportal-map-dialog.component';
import {MatProgressSpinnerModule} from '@angular/material/progress-spinner';
import { FilterPipe } from './geoportal-map/filter-full-list/filter.pipe';
import { HighlightDirective } from './geoportal-map/filter-full-list/highlight.pipe';
import { CanvasGraphComponent } from './geoportal-map/canvas-graph/canvas-graph.component';
import { NgxEchartsModule } from 'ngx-echarts';
import { DatePipe } from '@angular/common';
import { registerLocaleData } from '@angular/common';
import { NgxSliderModule } from '@angular-slider/ngx-slider';
import { LeafletModule } from "@asymmetrik/ngx-leaflet";
import localeFr from '@angular/common/locales/fr';
import localeIt from '@angular/common/locales/it';
import { GeoportalColorDialogComponent } from './geoportal-map/geoportal-color-dialog/geoportal-color-dialog.component';
import { InfoPageComponent } from './info-page/info-page.component';
import { CanvasGraphCompareComponent } from './geoportal-map/canvas-graph-compare/canvas-graph-compare.component';
import { GeoportalCompareDialogComponent } from './geoportal-map/geoportal-compare-dialog/geoportal-compare-dialog.component';
import { SelectCoordsDialogComponent } from './select-coords-dialog/select-coords-dialog.component';
import { AngularMatModule } from './modules/services/angular-mat/angular-mat.module';
import { PagesModule } from './modules/pages/pages.module';
import { GeoportalMapNewComponent } from './geoportal-map-new/geoportal-map-new.component';
import { GeoportalMapNewMenuComponent } from './geoportal-map-new-menu/geoportal-map-new-menu.component';
import { GeoportalMapMenuDialogComponent } from './geoportal-map-new-menu/geoportal-map-menu-dialog/geoportal-map-menu-dialog.component';
import { DemoLandingComponent } from './demo-landing/demo-landing.component';
registerLocaleData(localeFr);
registerLocaleData(localeIt);

@NgModule({
  declarations: [
    AppComponent,
    GeoportalMapComponent,
    GeoportalMapDialogComponent,
    FilterPipe, //added pipe filter
    HighlightDirective, //added directive highlight
    CanvasGraphComponent,
    GeoportalColorDialogComponent,
    InfoPageComponent,
    CanvasGraphCompareComponent,
    GeoportalCompareDialogComponent,
    SelectCoordsDialogComponent,
    GeoportalMapNewComponent,
    GeoportalMapNewMenuComponent,
    GeoportalMapMenuDialogComponent,
    DemoLandingComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    BrowserAnimationsModule,
    HttpClientModule,
    FlexLayoutModule,
    OverlayModule,
    ReactiveFormsModule,
    NgxEchartsModule.forRoot({
      echarts: () => import('echarts')
    }),
    LeafletModule,
    CdkListboxModule,
    PortalModule,
    ScrollingModule,
    CdkTreeModule,
    CdkMenuModule,
    NgxSliderModule,

    PagesModule,
    AngularMatModule,
    MatProgressSpinnerModule
  ],
  providers: [
    MatMenuTrigger,
    {provide: MAT_DATE_LOCALE, useValue: 'en-GB'},
    {provide: LOCALE_ID, useValue: 'fr-FR'},
    {provide: LOCALE_ID, useValue: 'it-IT'},
    DatePipe,

  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
