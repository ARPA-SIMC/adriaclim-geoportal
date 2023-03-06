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
}
