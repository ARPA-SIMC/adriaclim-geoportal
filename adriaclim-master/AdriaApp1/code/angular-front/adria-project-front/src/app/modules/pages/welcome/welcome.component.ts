import { Component } from '@angular/core';
import { Router } from '@angular/router';
import * as welcomeJson from '../../../../assets/configuration/welcomePage.json'

@Component({
  selector: 'app-welcome',
  templateUrl: './welcome.component.html',
  styleUrls: ['./welcome.component.scss']
})
export class WelcomeComponent {

  // title = welcomeJson["title"];
  // textContent = welcomeJson["text"];
  welJson = welcomeJson;
  constructor(private router: Router) {

  }

  /**
   * FUNZIONE CHE REINDIRIZZA ALLA MAPPA E RICARICA LA PAGINA PER MOSTRARE I POLIGONI
   */
  goToMap() {
    this.router.navigate(['/map']).then(() => {
      window.location.reload();
    });
  }

  /**
   * FUNZIONE CHE REINDIRIZZA AL LINK ESTERNO DEL WEB PROJECT
   */
  goToWebProject() {
    window.location.href = this.welJson.webProject;

  }

  /**
   * FUNZIONE CHE REINDIRIZZA AL LINK ESTERNO DEL TOOLKIT
   */
  goToToolkit() {
    window.location.href = this.welJson.toolkit;
  }

}
