import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { PagesComponent } from './pages.component';
import { WelcomeComponent } from './welcome/welcome.component';
import { DemoLandingComponent } from 'src/app/demo-landing/demo-landing.component';

const routes: Routes = [{ path: '', component: WelcomeComponent }];
// const routes: Routes = [
//   { path: '', component: DemoLandingComponent }
// ];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class PagesRoutingModule { }
