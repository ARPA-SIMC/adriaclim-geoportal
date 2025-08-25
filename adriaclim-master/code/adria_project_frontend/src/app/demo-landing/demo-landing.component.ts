import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import * as welcomeJson from '../../assets/configuration/welcomePage.json';
import { environmentDev, environmentProd, environmentDevProd } from 'src/assets/environments';

interface WelcomeJson {
  title: string;
  text: string;
  webProject: string;
  toolkit: string;
}

@Component({
  selector: 'app-demo-landing',
  templateUrl: './demo-landing.component.html',
  styleUrls: ['./demo-landing.component.scss']
})
export class DemoLandingComponent implements OnInit {
  welJson: WelcomeJson = welcomeJson;

  showCloud = false;
  showLightning = false;
  showButton = false;
  hideCloudAndLightning = false;

  constructor(private router: Router) {}

  ngOnInit(): void {
    this.showCloud = true;

    setTimeout(() => {
      this.showLightning = true;

      setTimeout(() => {
        this.showButton = true;

        // Avvia animazione di scomparsa
        this.hideCloudAndLightning = true;

        // Rimuove elementi dal DOM dopo il fade-out
        setTimeout(() => {
          this.showCloud = false;
          this.showLightning = false;
        }, 500); // poco più dei 0.4s di animazione
      }, 600);

    }, 1500);
  }

  goToMap() {
    this.router.navigate(['/mapNewMenu']).then(() => {
      window.location.reload();
    });
  }

  goToWebProject() {
    window.location.href = this.welJson.webProject;
  }

  goToToolkit() {
    window.location.href = this.welJson.toolkit;
  }
}
