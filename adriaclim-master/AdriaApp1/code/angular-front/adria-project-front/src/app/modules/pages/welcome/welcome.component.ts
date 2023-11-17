import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import * as welcomeJson from '../../../../assets/configuration/welcomePage.json'

interface WelcomeJson {
  title: string;
  text: string;
  webProject: string;
  toolkit: string;
}

@Component({
  selector: 'app-welcome',
  templateUrl: './welcome.component.html',
  styleUrls: ['./welcome.component.scss']
})
export class WelcomeComponent implements OnInit {

  // title = welcomeJson["title"];
  // textContent = welcomeJson["text"];
  welJson: WelcomeJson = welcomeJson;
  constructor(private router: Router) {

  }
  ngOnInit(): void {
    console.log("WELCOME JSON = ", welcomeJson);

    this.welJson = welcomeJson;
  }

  /**
   * Funzione che reindirizza alla mappa e ricarica la pagina per mostrare i poligoni
   */
  goToMap() {
    this.router.navigate(['/map']).then(() => {
      window.location.reload();
    });
  }

  /**
   * Funzione che reindirizza al link esterno del web project
   */
  goToWebProject() {
    window.location.href = this.welJson.webProject;

  }

  /**
   * Funzione che reinderizza al link esterno del toolkit
   */
  goToToolkit() {
    window.location.href = this.welJson.toolkit;
  }

}
