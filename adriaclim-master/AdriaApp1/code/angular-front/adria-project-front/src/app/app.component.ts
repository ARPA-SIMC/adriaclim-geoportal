import { HttpClient, HttpClientModule } from '@angular/common/http';
import { Component, OnInit, ViewEncapsulation } from '@angular/core';

const FUNCTION_CALLED_FLAG = 'function_called';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss'],
  encapsulation: ViewEncapsulation.None
})
export class AppComponent implements OnInit {
  title = 'adria-project-front';

  constructor(private httpClient: HttpClient) {
    // console.log('AppComponent constructor');
  }

  ngOnInit() {
    console.log('AppComponent ngOnInit');
    // this.getAllData();
    this.httpClient.post('http://localhost:8000/test/prova', {

    }).subscribe({
      next(position) {
        // console.log('Current Position: ', position);
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
    const orario = new Date(dataNow.getFullYear(), dataNow.getMonth(), dataNow.getDate(), 2, 0, 0, 0);
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
      console.log('Error ALL DATA: ', msg);
    }
  })
  }

 

}

export function initializeApp(appComponent: AppComponent) {
  return () => {
    // Check if the function has already been called
    const flag = localStorage.getItem(FUNCTION_CALLED_FLAG);
    if (!flag || flag !== 'true') {
      // Call the function at the start of the server
      appComponent.getAllData();

      // Set the flag to indicate that the function has been called
      localStorage.setItem(FUNCTION_CALLED_FLAG, 'true');
    }

    // Set the interval to call the function at a specific time every day
    const intervalId = setInterval(() => {
      const now = new Date();
      if (now.getHours() === 2 && now.getMinutes() === 0 && now.getSeconds() === 0) {
        // Reset the flag to allow the function to be called again
        localStorage.removeItem(FUNCTION_CALLED_FLAG);

        // Call the function
        appComponent.getAllData();
      }
    }, 1000); // Check every second

    // Clean up the interval on app exit
    window.addEventListener('beforeunload', () => clearInterval(intervalId));
  };
}