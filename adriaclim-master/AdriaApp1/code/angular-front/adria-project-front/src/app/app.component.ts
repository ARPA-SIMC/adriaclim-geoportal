import { HttpClient, HttpClientModule } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
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

    this.getPippo();

  }

  getPippo() {
    this.httpClient.post('http://localhost:8000/test/pippo', {

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
