import { Component } from '@angular/core';
import { Router } from '@angular/router';

interface OfficialResource {
  titleLine1: string;
  titleLine2: string;
  url: string;
  icon: string;
}

@Component({
  selector: 'app-welcome',
  templateUrl: './welcome.component.html',
  styleUrls: ['./welcome.component.scss']
})
export class WelcomeComponent {

  /**
   * Elenco delle risorse ufficiali mostrate nella sezione "Official Resources".
   * Per aggiungerne una nuova basta aggiungere un elemento a questo array.
   */
  resources: OfficialResource[] = [
    {
      titleLine1: 'AdriaClimPlus',
      titleLine2: 'Project page',
      url: 'https://www.italy-croatia.eu/web/adriaclimplus',
      icon: 'public'
    },
    {
      titleLine1: 'Climate Literacy',
      titleLine2: 'Toolkit',
      url: 'https://www.climateliteracy.eu/en/',
      icon: 'menu_book'
    },
    {
      titleLine1: 'AdriaClim',
      titleLine2: 'Project page',
      url: 'https://programming14-20.italy-croatia.eu/web/adriaclim',
      icon: 'groups'
    }
  ];

  /** Usato solo per disegnare le 12 stelle dell'emblema UE nel footer */
  euStars = Array(12).fill(0);

  constructor(private router: Router) { }

  /**
   * Funzione che reindirizza alla mappa e ricarica la pagina per mostrare i poligoni
   */
  goToMap() {
    this.router.navigate(['/mapNewMenu']).then(() => {
      window.location.reload();
    });
  }

}
