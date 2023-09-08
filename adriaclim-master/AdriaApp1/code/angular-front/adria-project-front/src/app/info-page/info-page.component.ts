import { Component } from '@angular/core';
import * as infoJson from "../../assets/configuration/infoModal.json"

@Component({
  selector: 'app-info-page',
  templateUrl: './info-page.component.html',
  styleUrls: ['./info-page.component.scss']
})
export class InfoPageComponent {

  info = infoJson;

}
