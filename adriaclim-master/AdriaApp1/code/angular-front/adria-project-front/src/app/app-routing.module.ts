import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { GeoportalMapComponent } from './geoportal-map/geoportal-map.component';
import { InfoPageComponent } from './info-page/info-page.component';
import { GeoportalMapNewComponent } from './geoportal-map-new/geoportal-map-new.component';
import { GeoportalMapNewMenuComponent } from './geoportal-map-new-menu/geoportal-map-new-menu.component';

const routes: Routes = [
  // { path: "", component: WelcomePageGeoportalComponent },
  { path: '', loadChildren: () => import('./modules/pages/pages.module').then(m => m.PagesModule) },
  { path: "map", component: GeoportalMapComponent },
  { path: "mapNew", component: GeoportalMapNewComponent },
  { path: "mapNewMenu", component: GeoportalMapNewMenuComponent },
  { path: "info", component: InfoPageComponent },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule {}
