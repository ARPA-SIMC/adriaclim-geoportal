import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { HttpClientModule } from '@angular/common/http';
import { GeoportalMapComponent } from './geoportal-map/geoportal-map.component';
import {MatButtonModule} from '@angular/material/button';
import { FlexLayoutModule } from '@angular/flex-layout';
import {MatCardModule} from '@angular/material/card';
import {MatToolbarModule} from '@angular/material/toolbar';
import {MatIconModule} from '@angular/material/icon';
import {MatExpansionModule} from '@angular/material/expansion';
import { MatMenuModule, MatMenuTrigger } from '@angular/material/menu';
import { OverlayModule } from '@angular/cdk/overlay';
import {MatFormFieldModule} from '@angular/material/form-field';
import {MatSelectModule} from '@angular/material/select';
import { ReactiveFormsModule } from '@angular/forms';
import {MatListModule} from '@angular/material/list';
import {MatTreeModule} from '@angular/material/tree';
import {MatRadioModule} from '@angular/material/radio';
import {MatNativeDateModule, MAT_DATE_LOCALE} from '@angular/material/core';

import {CdkListboxModule} from '@angular/cdk/listbox';
import {PortalModule} from '@angular/cdk/portal';
import {ScrollingModule} from '@angular/cdk/scrolling';
import {CdkTreeModule} from '@angular/cdk/tree';
import {MatBottomSheetModule} from '@angular/material/bottom-sheet';
import {MatButtonToggleModule} from '@angular/material/button-toggle';
import {MatCheckboxModule} from '@angular/material/checkbox';
import {CdkMenuModule} from '@angular/cdk/menu';
import { GeoportalMapDialogComponent } from './geoportal-map/geoportal-map-dialog/geoportal-map-dialog.component';
import {MatDialogModule} from '@angular/material/dialog';
import {MatProgressSpinnerModule} from '@angular/material/progress-spinner';
import {MatDividerModule} from '@angular/material/divider';
import {MatTooltipModule} from '@angular/material/tooltip';
import {MatDatepickerModule} from '@angular/material/datepicker';
import { MatInputModule } from '@angular/material/input';
import { FilterPipe } from './geoportal-map/filter-full-list/filter.pipe';
import { HighlightDirective } from './geoportal-map/filter-full-list/highlight.pipe';

@NgModule({
  declarations: [
    AppComponent,
    GeoportalMapComponent,
    GeoportalMapDialogComponent,
    FilterPipe, //added pipe filter
    HighlightDirective //added directive highlight
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    BrowserAnimationsModule,
    HttpClientModule,
    MatButtonModule,
    FlexLayoutModule,
    MatCardModule,
    MatToolbarModule,
    MatIconModule,
    MatExpansionModule,
    MatMenuModule,
    OverlayModule,
    MatFormFieldModule,
    MatSelectModule,
    ReactiveFormsModule,
    MatListModule,
    MatTreeModule,
    MatRadioModule,

    MatNativeDateModule,
    CdkListboxModule,
    PortalModule,
    ScrollingModule,
    CdkTreeModule,
    CdkMenuModule,
    MatBottomSheetModule,
    MatButtonToggleModule,
    MatCheckboxModule,
    MatDialogModule,
    MatProgressSpinnerModule,
    MatDividerModule,
    MatTooltipModule,
    MatDatepickerModule,
    MatInputModule,

  ],
  providers: [
    MatMenuTrigger,
    {provide: MAT_DATE_LOCALE, useValue: 'en-GB'}
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
