import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { GeoportalMapComponent } from './geoportal-map/geoportal-map.component';
import { InfoPageComponent } from './info-page/info-page.component';
import { GeoportalMapNewComponent } from './geoportal-map-new/geoportal-map-new.component';

const routes: Routes = [
  // { path: "", component: WelcomePageGeoportalComponent },
  { path: '', loadChildren: () => import('./modules/pages/pages.module').then(m => m.PagesModule) },
  { path: "map", component: GeoportalMapComponent },
  { path: "mapNew", component: GeoportalMapNewComponent },
  { path: "info", component: InfoPageComponent },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule {}
