import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { GeoportalMapComponent } from './geoportal-map/geoportal-map.component';
import { InfoPageComponent } from './info-page/info-page.component';
import { WelcomePageGeoportalComponent } from './welcome-page-geoportal/welcome-page-geoportal.component';

const routes: Routes = [
  { path: "", component: WelcomePageGeoportalComponent },
  { path: "map", component: GeoportalMapComponent },
  { path: "info", component: InfoPageComponent },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule {}
