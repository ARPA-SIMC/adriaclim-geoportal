import { HttpClient, HttpClientModule } from '@angular/common/http';
import { AfterViewInit, Component, OnInit, ViewEncapsulation } from '@angular/core';

const FUNCTION_CALLED_FLAG = 'function_called';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss'],
  encapsulation: ViewEncapsulation.None
})
export class AppComponent implements OnInit, AfterViewInit {
  title = 'adria-project-front';

  constructor(private httpClient: HttpClient) {
    // console.log('AppComponent constructor');
  }

  ngAfterViewInit(): void {



  }
  ngOnInit() {
    console.log('AppComponent ngOnInit');
    // this.getAllData();
    // this.httpClient.post('http://localhost:8000/test/prova', {

    // }).subscribe({
    //   next(position) {
    //     // console.log('Current Position: ', position);
    //   },
    //   error(msg) {
    //     console.log('Error Getting Location: ', msg);
    //   }
    // });

    // this.getPippo("ciao");

    /**
     *  LANCIO DELLA FUNZIONE ALL'ORARIO PREDEFINITO
     */
    console.log("PRIMA");
    const dataNow = new Date();
    const orario = new Date(dataNow.getFullYear(), dataNow.getMonth(), dataNow.getDate(), 16, 35, 0, 0);
    console.log('dataNow: ', dataNow);
    console.log('orario: ', orario);
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
        // console.log('PIPPO: ', position);
      },
      error(msg) {
        // console.log('PIPPO ERROR: ', msg);
      }
    });
  }

  getAllData(){
    this.httpClient.post('http://localhost:8000/myFunctions/getAllDatasets', {
  }).subscribe({
    next(position) {

    },
    error(msg) {
      // console.log('Error ALL DATA: ', msg);
    }
  })
  }



}

