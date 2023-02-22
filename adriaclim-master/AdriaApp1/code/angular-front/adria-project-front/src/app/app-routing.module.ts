import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { GeoportalMapComponent } from './geoportal-map/geoportal-map.component';

const routes: Routes = [
  { path: "", component: GeoportalMapComponent },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule {}
