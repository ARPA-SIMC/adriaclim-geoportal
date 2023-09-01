import { HttpClient } from '@angular/common/http';
import { Component, OnInit, ViewEncapsulation } from '@angular/core';
import { HttpService } from './services/http.service';


@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss'],
  encapsulation: ViewEncapsulation.None
})
export class AppComponent implements OnInit {
  title = 'adria-project-front';

  constructor(private httpClient: HttpClient, private httpService: HttpService) { }

  ngOnInit() {
    // console.log('Ready');
    console.debug('Ready');
    // this.getAllData();
    //this.getMBIndicator("monthly"); //2138.8134632110596 MB per yearly, 8442.947506904602  MB seasonal, 25252.07095527649  MB monthly

    /**
     *  LANCIO DELLA FUNZIONE ALL'ORARIO PREDEFINITO
     */
    // console.log("PRIMA");
    // const dataNow = new Date();
    // const orario = new Date(dataNow.getFullYear(), dataNow.getMonth(), dataNow.getDate(), 16, 35, 0, 0);
    // console.log('dataNow: ', dataNow);
    // console.log('orario: ', orario);
    // const tempoRimanente = orario.getTime() - dataNow.getTime();
    // console.log('tempoRimanente: ', tempoRimanente);

    // if(tempoRimanente > 0) {
    //   setTimeout(() => {
    // this.getAllData();
    //   }, tempoRimanente);
    // }

  }

  /**
   * FUNZIONE DA RICHIAMARE NELL'NGONINIT SOLO PER AGGIORNARE I DATI LATO SVILUPPO QUANDO SERVE POI COMMENTARE
   */
  getAllData() {
    this.httpService.post('myFunctions/getAllDatasets', {
    }).subscribe({
      next(position: any) {
        console.log("ALL DATA OK");

      },
      error(msg: any) {
        // console.log('Error ALL DATA: ', msg);
      }
    })
  }

  getMBIndicator(timeperiod: string) {
    this.httpService.post('test/discover_mb', {
      timeperiod: timeperiod
    }).subscribe({
      next(position: any) {
        console.log("MB_SIZE=======", position)
      },
      error(msg: any) {
        // console.log('Error ALL DATA: ', msg);
      }
    })
  }

}

