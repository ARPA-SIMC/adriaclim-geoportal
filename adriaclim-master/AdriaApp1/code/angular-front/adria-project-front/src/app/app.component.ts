import { HttpClient, HttpClientModule } from '@angular/common/http';
import { Component, OnInit, ViewEncapsulation } from '@angular/core';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss'],
  encapsulation: ViewEncapsulation.None
})
export class AppComponent implements OnInit {
  title = 'adria-project-front';

  constructor(private httpClient: HttpClient) {
    console.log('AppComponent constructor');
  }

  ngOnInit() {
    console.log('AppComponent ngOnInit');
    // this.getAllData();
    this.httpClient.post('http://localhost:8000/test/prova', {

    }).subscribe({
      next(position) {
        console.log('Current Position: ', position);
      },
      error(msg) {
        console.log('Error Getting Location: ', msg);
      }
    });

    this.getPippo("ciao");

    /**
     *  LANCIO DELLA FUNZIONE ALL'ORARIO PREDEFINITO
     */
    const dataNow = new Date();
    const orario = new Date(dataNow.getFullYear(), dataNow.getMonth(), dataNow.getDate(), 3, 0, 0, 0);
    const tempoRimanente = orario.getTime() - dataNow.getTime();
    console.log('tempoRimanente: ', tempoRimanente);

    if(tempoRimanente > 0) {
      setTimeout(() => {
        this.getAllData();
      }, tempoRimanente);
    }

  }

  getPippo(idInput: string) {
    this.httpClient.post('http://localhost:8000/test/pippo', {
      inputEsterno: idInput
    }).subscribe({
      next(position) {
        console.log('PIPPO: ', position);
      },
      error(msg) {
        console.log('PIPPO ERROR: ', msg);
      }
    });
  }

  getAllData(){
    this.httpClient.post('http://localhost:8000/myFunctions/getAllDatasets', {
  }).subscribe({
    next(position) {
    },
    error(msg) {
    }
  })
  }

}
