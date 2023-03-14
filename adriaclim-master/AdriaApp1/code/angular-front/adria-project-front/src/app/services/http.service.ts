import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class HttpService {

  // httpOptions: any = {
  //   headers: new HttpHeaders({
  //     'Content-Type': 'application/json',
  //     'Access-Control-Allow-Origin': '*',
  //   })
  // }
  headers = new HttpHeaders()
    .set('Content-Type', 'application/json; charset=utf-8')
    .set('Access-Control-Allow-Origin', 'http://localhost:4200/')

  constructor(private httpClient: HttpClient) { }



  downloadFile(): any {
		return this.httpClient.get("https://erddap-adriaclim.cmcc-opa.eu/erddap/griddap/atm_regional_4d78_6f74_63bc.json?wind10m%5B(1969-12-30T00:00:00Z):1:(2005-11-20T00:00:00Z)%5D%5B(42.87742828483367):1:(42.87742828483367)%5D%5B(11.656494140625002):1:(11.656494140625002)%5D",
     {headers: this.headers, responseType: 'blob'});
  }

}
