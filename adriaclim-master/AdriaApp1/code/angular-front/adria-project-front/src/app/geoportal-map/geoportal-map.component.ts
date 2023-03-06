import { FlatTreeControl, NestedTreeControl } from '@angular/cdk/tree';
import { HttpClient } from '@angular/common/http';
import { AfterViewInit, Component, ElementRef, OnInit, ViewChild } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import { MatDialogConfig, MatDialog } from '@angular/material/dialog';
import { MatMenuTrigger } from '@angular/material/menu';
import { MatTreeFlatDataSource, MatTreeFlattener, MatTreeNestedDataSource } from '@angular/material/tree';
import * as L from 'leaflet';
import { latLng, marker, Marker, icon } from 'leaflet';
import { map } from 'rxjs';
import * as poly from '../../assets/geojson/geojson.json';
import { GeoportalMapDialogComponent } from './geoportal-map-dialog/geoportal-map-dialog.component';
import * as _ from 'lodash';
import * as moment from 'moment';

/**
 * Food data with nested structure.
 * Each node has a name and an optional list of children.
 */
interface FoodNode {
  name: string;
  value?: string;
  childVisible?: boolean;
  children?: FoodNode[];
}
interface ExtendedWMSOptions extends L.TileLayerOptions {
  bgcolor?: string;
  time?: string;
}

// const TREE_DATA: FoodNode[] = [
//   {
//     name: 'Fruit',
//     children: [{name: 'Apple'}, {name: 'Banana'}, {name: 'Fruit loops'}],
//   },
//   {
//     name: 'Vegetables',
//     children: [
//       {
//         name: 'Green',
//         children: [{name: 'Broccoli'}, {name: 'Brussels sprouts'}],
//       },
//       {
//         name: 'Orange',
//         children: [{name: 'Pumpkins'}, {name: 'Carrots'}],
//       },
//     ],
//   },
// ];

let TREE_DATA: FoodNode[] = [
    {
      name: 'Observations',
      childVisible: false,
      children: [],
    },
    {
      name: 'Indicators',
      childVisible: true,
      children: [
        {
          name: 'Large scale',
          childVisible: true,
          children: [
            {name: 'Yearly', childVisible: true, children: []},
            {name: 'Monthly', childVisible: false, children: []},
            {name: 'Seasonal', childVisible: false, children: []}
          ],
        },
        {
          name: 'Pilot scale',
          childVisible: true,
          children: [
            {name: 'Yearly', childVisible: false, children: []},
            {name: 'Monthly', childVisible: false, children: []},
            {name: 'Seasonal', childVisible: false, children: []}
          ],
        },
        {
          name: 'Local scale',
          childVisible: true,
          children: [
            {name: 'Yearly', childVisible: false, children: []},
            {name: 'Monthly', childVisible: false, children: []},
            {name: 'Seasonal', childVisible: false, children: []}
          ],
        },
      ],
    },
    {
      name: 'Numerical models',
      children: [],
    },
    {
      name: 'Full list',
      children: [],
    },
  ];

/** Flat node with expandable and level information */
interface ExampleFlatNode {
  expandable: boolean;
  name: string;
  level: number;
}

@Component({
  selector: 'app-geoportal-map',
  templateUrl: './geoportal-map.component.html',
  styleUrls: ['./geoportal-map.component.scss']
})
export class GeoportalMapComponent implements OnInit, AfterViewInit {

  panelOpenState = false;

  @ViewChild('map') mapContainer!: ElementRef;
  map!: L.Map;
  // centroid: L.LatLngExpression = [41.9027835, 12.4963655]; // Roma
  center: L.LatLngExpression = [42.744388161339, 12.0809380292276]; // Centro Italia
  zoom = 7;

  markersLayer: L.LayerGroup = L.layerGroup(); // crea un nuovo layerGroup vuoto

  markers: L.Marker[] = [];

  polygon = poly;

  dataInd: any;
  dataAllNodes: any[] = [];

  selData: FormGroup;
  selectedDate: FormGroup;
  variableGroup: FormGroup;
  nodeSelected: any;

  metadata: any;
  dateStart: any;
  dateEnd: any;
  variableArray: [] = [];

  ERDDAP_URL = "https://erddap-adriaclim.cmcc-opa.eu/erddap";
  legendLayer_src: any;
  datasetLayer: any;

  navigateDateLeftYear = false;
  navigateDateRightYear = true;
  navigateDateLeftMonth = false;
  navigateDateRightMonth = true;
  navigateDateLeftSeason = false;
  navigateDateRightSeason = true;

  constructor(private httpClient: HttpClient, private dialog: MatDialog) {
    this.selData = new FormGroup({
      dataSetSel: new FormControl(),
      searchText: new FormControl()
    });
    this.selectedDate = new FormGroup({
      dateSel: new FormControl()
    });
    this.variableGroup = new FormGroup({
      variableControl: new FormControl(null)
    });

    this.getInd();
    this.getAllNodes();
    // this.dataSource.data = TREE_DATA;

  }

  async ngAfterViewInit(): Promise<void> {

    // this.landLayers();
    // console.log("POLYGON JSON =", this.polygon);
    // console.log("POL ==", this.polygon.features[0].geometry.coordinates[0]);

    // let geo = L.geoJSON(this.polygon).addTo(this.map);


    let polyg: any = [];
    this.polygon.features.forEach(f => {
      // console.log("FEATURE =", f);
      if(f.properties.popupContent !== "") {

        f.geometry.coordinates.forEach(c => {
          // console.log("COORDINATE =", c);
          c.forEach(coord => {
            coord.reverse();
            // console.log("COORDINATE 2 =", coord);
          });

          polyg.push(c);
          // poligon = L.polygon(c);
        });
        // console.log("POLYGON =", polyg[0]);

        let pol = L.polygon(polyg[0]).addTo(this.map);
        polyg = [];
      }
    });
    // .addTo(this.map);
    // const polygo = L.polygon(
    //   [
    //     [43.34471993041581, 10.695002224139875],
    //     [43.06626090251556, 11.585015616399813],
    //     [42.616704865269284, 11.4120295594627],
    //     [42.61546062315476, 10.695002224139875],
    //   ],
    // ).addTo(this.map);
    this.getPluto();

  }

  async ngOnInit(): Promise<void> {
    await this.initMap();


    // await this.initMap();
    // console.log("POLYGON =", this.polygon.features);
    // console.log("PROVA");

  }

  async initMap(): Promise<void> {
    this.map = L.map("map").setView(this.center, this.zoom);

    // imposto il layer della mappa prendendolo da openstreetmap assegnando i valori di zoom massimi e minimi
    const tiles = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 18,
      minZoom: 1,
      attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    });

    tiles.addTo(this.map);

    // assegno la funzione al click sulla mappa per generare il marker
    this.map.on('click', this.onMapClick.bind(this));

    // ASSEGNO DEI VALORI E GENERO UN POLIGONO


  }

  // addPolygons() {

  // }

  // metodo richiamato al click sulla mappa
  onMapClick = (e: L.LeafletMouseEvent) => {
    // console.log("EVENT ON CLICK =", e);

    // imposto la lat e long del marker e le dimensioni della sua icona
    // METODO 1
    // let marker = null;
    // marker = L.marker(e.latlng, {
    //   icon: L.icon({
    //     iconSize: [25, 41],
    //     iconAnchor: [13, 41],
    //     iconUrl: 'marker-icon.png',
    //   })
    // }).addTo(this.map);

    // METODO 2
    const marker = L.marker(e.latlng, {
      icon: L.icon({
          iconSize: [25, 41],
          iconAnchor: [13, 41],
          iconUrl: 'marker-icon.png',
      })
    });
    marker.on('click', this.onMarkerClick.bind(this));
    marker.addTo(this.map);
    this.markers.push(marker);
    // this.markersLayer.addLayer(marker);
    // this.markersLayer.addTo(this.map);

    // console.log("MARKER =", marker);
    // console.log("MAP =", this.map);
  }


  onMarkerClick(event: any) {
    const marker = event.target;
    // console.log("MARKER CLICKED =", marker);

    this.map.removeLayer(marker);
    this.markers = this.markers.filter(m => m !== marker);
  }

  openMyMenu(menuTrigger: MatMenuTrigger) {
    // console.log("MENU TRIGGER =", menuTrigger);

    // menuTrigger.openMenu();
    menuTrigger.openMenu();
  }

  closeMyMenu(menuTrigger: MatMenuTrigger) {
    menuTrigger.closeMenu();
  }

  getPluto() {
    this.httpClient.post('http://localhost:8000/test/pluto', {
    }).subscribe({
      next(position) {
        // console.log('PLUTO: ', position);
      },
      error(msg) {
        // console.log('PLUTO ERROR: ', msg);
      }
    });
  }

  getAllNodes(){
    this.httpClient.post('http://localhost:8000/test/allNodes',{
    }).subscribe({
      next:(res:any) =>{
        res.nodes.forEach((node:any)=>{

          this.dataAllNodes.push(
            {name: node}
          );

        });

        this.dataAllNodes.sort((o1, o2) => {
          if (o1.name.title > o2.name.title) {
            return 1;
          }
          if (o1.name.title < o2.name.title) {
            return -1;
          }
          return 0;
        })

      },
      error: (msg: any) => {
        console.log('ALL NODES ERROR: ',msg);
      }
    })
  }

  getInd() {
    // this.httpClient.post('http://localhost:8000/test/ind', {
    // }).pipe(map((res: any) => res.json())).subscribe({
    //   next(res) {
    //     console.log('IND: ', res);
    //     this.dataInd = res;
    //   },
    //   error(msg) {
    //     console.log('IND ERROR: ', msg);
    //   }

    // });
    this.httpClient.post('http://localhost:8000/test/ind', {
    }).subscribe({
      next: (res: any) => {
        // console.log('IND: ', res);

        this.dataInd = res.ind;
        // console.log("INDICATORI =", this.dataInd);


        this.dataInd.forEach((ind: any) => {
          let indicatori = TREE_DATA.filter((node: any) => node.name === "Indicators")[0]
          let scale = indicatori.children?.filter((sca: any) => sca.name.toLowerCase().includes(ind.adriaclim_scale.toLowerCase()))[0];
          let time = scale?.children?.filter((time: any) => time.name.toLowerCase().includes(ind.adriaclim_timeperiod.toLowerCase()))[0];
          if(time?.children?.findIndex(title => title.name === ind.title) === -1) {
            time?.children?.push({
              name: ind
            });
            time.childVisible = true;
          }

            // console.log("INDICATORI ESISTE");
            // console.log("TREE DATA =", indicatori);
            // console.log("TREE DATA =", scale);
            // console.log("TREE DATA =", time);


          // TREE_DATA.filter((node: any) => node.name === "Indicators")[0]
          //   .children?.filter((sca: any) => sca.name.toLowerCase().includes(ind.adriaclim_scale.toLowerCase()))[0]
          //   .children?.filter((time: any) => time.name.toLowerCase().includes(ind.adriaclim_timeperiod.toLowerCase()))[0].children?.push({
          //     name: ind.title
          //   })



          });

          // console.log("TREE DATA =", TREE_DATA);
          this.dataSource.data = TREE_DATA;
      },
      error: (msg: any) => {
        // console.log('IND ERROR: ', msg);
      }

    });

  }

  getMeta(idMeta: any, controlDate?: any) {

    console.log("ID METADATA =", idMeta);
    console.log("CONTROL DATE =", controlDate);


    if(this.legendLayer_src) {
      this.deleteLayer(idMeta);

    }
    this.httpClient.post('http://localhost:8000/test/metadata', {
      idMeta: idMeta
    }).subscribe({
      next: (res: any) => {
        // console.log('METADATA: ', res);
        this.metadata = res;
        if(controlDate === "ok") {

          this.getLayers(idMeta, controlDate);
        }
        else {
          this.getLayers(idMeta);
        }
      },
      error: (msg: any) => {
        // console.log('METADATA ERROR: ', msg);
      }

    });

  }

  getSelectedNode(node: any) {
    // console.log("NODE =", node.name.variable_names);
    this.variableArray = node.name.variable_names.split(" ");
    // console.log("COSA C'E' QUI ==", this.selData.get("dataSetSel")?.value);
    // this.variableGroup.get("variableControl")?.setValue()
    // console.log("VARIABLE ARRAY =", this.variableArray);

  }

  // myFilter (d: Date | null, dateStart: any, dateEnd: any): boolean {
  //   const date = (d || new Date());
  //   console.log("DATE ==", date);
  //   console.log("DATE START ==", dateStart);
  //   console.log("DATE END ==", dateEnd);

  //   return date >= dateStart && date <= dateEnd;
  // };

  lastday(y:any,m:any){
    console.log("LAST DAY ==", new Date(y, m + 1, 0).getDate());

    return  new Date(y, m + 1, 0).getDate();
  }

//addRealMonth will return the real next month!
 addRealMonth(d:any,months:any) {
    var fm = moment(d).add(months, 'M');
    var fmEnd = moment(fm).endOf('month');
    return d.date() != fm.date() && fm.isSame(fmEnd.format('YYYY-MM-DD')) ? fm.add(1, 'd') : fm;
  }

  //subtractRealMonth will return the real month before!
  subtractRealMonth(d:any, months: any) {
    var fm = moment(d).subtract(months, 'M');
    var fmEnd = moment(fm).endOf('month');
    return d.date() != fm.date() && fm.isSame(fmEnd.format('YYYY-MM-DD')) ? fm.add(1, 'd') : fm;
  }

  subtractLastDayMonth(d:any,months:any){
    return moment(d).subtract(months, 'months').endOf('month').toDate();
  }

  addLastDayMonth(d:any,months:any){
    return moment(d).add(months, 'months').endOf('month').toDate();
  }

  isLastDayOfMonth(d:any){
    d.setDate(d.getDate()+1);
    if (d.getDate() === 1){
      return true;
    }else{
      return false;
    }
  }


  changeDate(arrow: any) {

    // let selD = _.cloneDeep(this.selectedDate.get("dateSel")?.value);
    // console.log("LEFT DATE ==", this.selectedDate.get("dateSel")?.value.getTime());
    // console.log("LEFT DATE CLONE ==", selD.getTime());

    // console.log("DATE START ==", this.dateStart.getTime());
    // if(selD.getTime() === this.dateStart.getTime()) {


    //   this.navigateDateLeftYear = true;
    // }
    // else if(selD.getTime() === this.dateEnd.getTime()) {
    //   this.navigateDateRightYear = true;
    // }

    if(arrow === "leftAll") {
      this.selectedDate.get("dateSel")?.setValue(this.dateStart);
      //leftAll is clicked so we disable left button and enable the right ones
      this.navigateDateLeftYear = true;
      this.navigateDateRightYear = false;
      this.navigateDateRightMonth = false;
      this.navigateDateRightSeason = false;
      this.navigateDateLeftMonth = false;
      this.navigateDateLeftSeason = false;
      this.getMeta(this.selData.get("dataSetSel")?.value.name.dataset_id,"ok");
    }
    else if(arrow === "rightAll") {
      //rightAll is clicked so we disable right button and enable the left ones
      this.selectedDate.get("dateSel")?.setValue(this.dateEnd);
      this.navigateDateRightYear = true;
      this.navigateDateLeftYear = false;
      this.navigateDateLeftSeason = false;
      this.navigateDateLeftMonth = false;
      this.navigateDateRightMonth = false;
      this.navigateDateRightSeason = false;
      this.getMeta(this.selData.get("dataSetSel")?.value.name.dataset_id,"ok");
    }
/**
 * GET LAYER 3D
 */
/**
 * SLIDER
 */
    if(this.selData.get("dataSetSel")?.value.name.adriaclim_timeperiod === "yearly") {
      if(arrow === "left") {

        let selD = _.cloneDeep(this.selectedDate.get("dateSel")?.value);
        if((selD.getFullYear()-1 ) === this.dateStart.getFullYear()){
          //it is the first year visible so after setting the new value we disable the left button
          selD.setFullYear(selD.getFullYear() - 1);
          this.selectedDate.get("dateSel")?.setValue(selD);
          this.navigateDateLeftYear = true;
          this.navigateDateRightYear = false;
          this.navigateDateRightMonth = false;
          this.navigateDateRightSeason = false;
          this.getMeta(this.selData.get("dataSetSel")?.value.name.dataset_id,"ok");
        }else{
          selD.setFullYear(selD.getFullYear() - 1);
          this.selectedDate.get("dateSel")?.setValue(selD);
          this.navigateDateLeftYear = false;
          this.navigateDateRightYear = false;
          this.navigateDateRightMonth = false;
          this.navigateDateRightSeason = false;
          this.getMeta(this.selData.get("dataSetSel")?.value.name.dataset_id,"ok");
        }
      }
      else if(arrow === "right") {
        let selD = _.cloneDeep(this.selectedDate.get("dateSel")?.value);
        if((selD.getFullYear() + 1) === this.dateEnd.getFullYear()){
          selD.setFullYear(selD.getFullYear() + 1);
          this.selectedDate.get("dateSel")?.setValue(selD);
          this.navigateDateRightYear = true;
          this.navigateDateLeftYear = false;
          this.getMeta(this.selData.get("dataSetSel")?.value.name.dataset_id,"ok");
        }else{
          selD.setFullYear(selD.getFullYear() + 1);
          this.selectedDate.get("dateSel")?.setValue(selD);
          this.navigateDateRightYear = false;
          this.navigateDateLeftYear = false;
          this.getMeta(this.selData.get("dataSetSel")?.value.name.dataset_id,"ok");
        }

      }
    }
    else if(this.selData.get("dataSetSel")?.value.name.adriaclim_timeperiod === "monthly") {
      if(arrow === "left") {
        let selD = _.cloneDeep(this.selectedDate.get("dateSel")?.value);
        // console.log(selD);
        let d1 = _.cloneDeep(selD);
        if(this.isLastDayOfMonth(d1)){
          console.log("ULTIMO GIORNO DEL MESEEEEEEEEEEEEE!");
        //SIAMO ALL'ULTIMO GIORNO DEL MESE, GESTIRE QUESTO CASO
          let d2 = _.cloneDeep(selD);
          d2 = this.subtractLastDayMonth(d2, 1);
          d2.setHours(this.dateStart.getHours(),this.dateStart.getMinutes(),this.dateStart.getSeconds());
          if(d2.toString() === this.dateStart.toString()){
              //ULTIMO GIORNO DEL MESE E PRIMA DATA!
              selD = d2;
              this.selectedDate.get("dateSel")?.setValue(selD);
              this.navigateDateLeftMonth = true;
              this.navigateDateRightMonth = false;
              this.navigateDateRightSeason = false;
              this.navigateDateRightYear = false;
              this.navigateDateLeftYear = false;
              this.navigateDateLeftSeason = false;
              this.getMeta(this.selData.get("dataSetSel")?.value.name.dataset_id,"ok");
          }else{
            selD = d2;
            this.selectedDate.get("dateSel")?.setValue(selD);
            this.navigateDateLeftMonth = false;
            this.navigateDateRightMonth = false;
            this.navigateDateRightSeason = false;
            this.navigateDateRightYear = false;
            this.navigateDateLeftYear = false;
            this.navigateDateLeftSeason = false;
            this.getMeta(this.selData.get("dataSetSel")?.value.name.dataset_id,"ok");
          }


        } else{
          //NON SIAMO ALL'ULTIMO GIORNO DEL MESE!
          let d2 = _.cloneDeep(selD);
          d2 = this.subtractRealMonth(moment(d2), 1).toDate();
          d2.setHours(this.dateStart.getHours(),this.dateStart.getMinutes(),this.dateStart.getSeconds());
          if(d2.toString() === this.dateStart.toString()){
            //ULTIMA DATA!
            selD = d2;
            this.selectedDate.get("dateSel")?.setValue(selD);
            this.navigateDateLeftMonth = true;
            this.navigateDateRightMonth = false;
            this.navigateDateRightSeason = false;
            this.navigateDateRightYear = false;
            this.navigateDateLeftYear = false;
            this.navigateDateLeftSeason = false;
            this.getMeta(this.selData.get("dataSetSel")?.value.name.dataset_id,"ok");
          }else{
            selD = d2;
            this.selectedDate.get("dateSel")?.setValue(selD);
            this.navigateDateLeftMonth = false;
            this.navigateDateRightMonth = false;
            this.navigateDateRightSeason = false;
            this.navigateDateRightYear = false;
            this.navigateDateLeftYear = false;
            this.navigateDateLeftSeason = false;
            this.getMeta(this.selData.get("dataSetSel")?.value.name.dataset_id,"ok");
          }
        }
      }
      else if(arrow === "right") {

        let selD = _.cloneDeep(this.selectedDate.get("dateSel")?.value);
        let d1 = _.cloneDeep(selD);
        if(this.isLastDayOfMonth(d1)){
          console.log("ULTIMO GIORNO DEL MESEEEEEEEEEEEEE!");
        //SIAMO ALL'ULTIMO GIORNO DEL MESE, GESTIRE QUESTO CASO
          let d2 = _.cloneDeep(selD);
          d2 = this.addLastDayMonth(d2,1);
          d2.setHours(this.dateEnd.getHours(),this.dateEnd.getMinutes(),this.dateEnd.getSeconds());
          if(d2.toString() === this.dateEnd.toString()){
              //ULTIMO GIORNO DEL MESE E PRIMA DATA!
              selD = d2;
              this.selectedDate.get("dateSel")?.setValue(selD);
              this.navigateDateLeftMonth = false;
              this.navigateDateRightMonth = true;
              this.navigateDateRightSeason = false;
              this.navigateDateRightYear = false;
              this.navigateDateLeftYear = false;
              this.navigateDateLeftSeason = false;
              this.getMeta(this.selData.get("dataSetSel")?.value.name.dataset_id,"ok");
          }else{
            selD = d2;
            this.selectedDate.get("dateSel")?.setValue(selD);
            this.navigateDateLeftMonth = false;
            this.navigateDateLeftYear = false;
            this.navigateDateLeftSeason = false;
            this.navigateDateRightMonth = false;
            this.navigateDateRightSeason = false;
            this.navigateDateRightYear = false;
            this.getMeta(this.selData.get("dataSetSel")?.value.name.dataset_id,"ok");
          }


        } else{
          //NON SIAMO ALL'ULTIMO GIORNO DEL MESE!
          let d2 = _.cloneDeep(selD);
          d2 = this.addRealMonth(moment(d2), 1).toDate();
          d2.setHours(this.dateEnd.getHours(),this.dateEnd.getMinutes(),this.dateEnd.getSeconds());
          if(d2.toString() === this.dateEnd.toString()){
            //ULTIMA DATA!
            selD = d2;
            console.log(selD);
            this.selectedDate.get("dateSel")?.setValue(selD);
            this.navigateDateLeftMonth = false;
            this.navigateDateRightMonth = true;
            this.navigateDateRightSeason = false;
            this.navigateDateRightYear = false;
            this.navigateDateLeftYear = false;
            this.navigateDateLeftSeason = false;
            this.getMeta(this.selData.get("dataSetSel")?.value.name.dataset_id,"ok");
          }else{
            selD = d2;
            this.selectedDate.get("dateSel")?.setValue(selD);
            this.navigateDateLeftMonth = false;
            this.navigateDateLeftYear = false;
            this.navigateDateLeftSeason = false;
            this.navigateDateRightMonth = false;
            this.navigateDateRightSeason = false;
            this.navigateDateRightYear = false;
            this.getMeta(this.selData.get("dataSetSel")?.value.name.dataset_id,"ok");
          }
        }
      }
    }
    else if(this.selData.get("dataSetSel")?.value.name.adriaclim_timeperiod === "seasonal") {
      if(arrow === "left") {
        let selD = _.cloneDeep(this.selectedDate.get("dateSel")?.value);
        //if(selD.getMonth() === 0) { //NON VA FATTO QUESTO CHECK!!!!
          // selD.setMonth(9);
          // selD.setFullYear(selD.getFullYear() - 1);
          let d1 = _.cloneDeep(selD);
          if(this.isLastDayOfMonth(d1)){
            //SIAMO ALL'ULTIMO GIORNO DEL MESE!!!!!!!!!
            let d2 = _.cloneDeep(selD);
            d2 = this.subtractLastDayMonth(d2,3);
            d2.setHours(this.dateStart.getHours(),this.dateStart.getMinutes(),this.dateStart.getSeconds());
            if(d2 <= this.dateStart) {
              selD = d2;
              this.selectedDate.get("dateSel")?.setValue(selD);
              this.navigateDateLeftMonth = false;
              this.navigateDateLeftYear = false;
              this.navigateDateLeftSeason = true;
              this.navigateDateRightMonth = false;
              this.navigateDateRightSeason = false;
              this.navigateDateRightYear = false;
              this.getMeta(this.selData.get("dataSetSel")?.value.name.dataset_id,"ok");

            }else{
              selD = d2;
              this.selectedDate.get("dateSel")?.setValue(selD);
              this.navigateDateLeftMonth = false;
              this.navigateDateLeftYear = false;
              this.navigateDateLeftSeason = false;
              this.navigateDateRightMonth = false;
              this.navigateDateRightSeason = false;
              this.navigateDateRightYear = false;
              this.getMeta(this.selData.get("dataSetSel")?.value.name.dataset_id,"ok");
            }

          }else{
            //NON SIAMO ALL'ULTIMO GIORNO DEL MESE
            let d2 = _.cloneDeep(selD);
            d2 = this.subtractRealMonth(moment(d2), 3).toDate();
            d2.setHours(this.dateStart.getHours(),this.dateStart.getMinutes(),this.dateStart.getSeconds());
            if(d2 <= this.dateStart){
              //ULTIMA DATA!
              selD = d2;
              this.selectedDate.get("dateSel")?.setValue(selD);
              this.navigateDateLeftMonth = false;
              this.navigateDateRightMonth = false;
              this.navigateDateRightSeason = false;
              this.navigateDateRightYear = false;
              this.navigateDateLeftYear = false;
              this.navigateDateLeftSeason = true;
              this.getMeta(this.selData.get("dataSetSel")?.value.name.dataset_id,"ok");
            }else{
              selD = d2;
              this.selectedDate.get("dateSel")?.setValue(selD);
              this.navigateDateLeftMonth = false;
              this.navigateDateRightMonth = false;
              this.navigateDateRightSeason = false;
              this.navigateDateRightYear = false;
              this.navigateDateLeftYear = false;
              this.navigateDateLeftSeason = false;
              this.getMeta(this.selData.get("dataSetSel")?.value.name.dataset_id,"ok");
            }
          }

        //} //CHECK PER VEDERE SE ERAVAMO A GENNAIO CHE POSSIAMO TOGLIERE!!!

        // else {
        //   selD.setMonth(selD.getMonth() - 3);
        //   if(selD < this.dateStart){
        //     this.navigateDateLeftSeason = true;
        //   }else{
        //     this.selectedDate.get("dateSel")?.setValue(selD);
        //     this.navigateDateLeftSeason = false;
        //   }
        // }

      } //FINE ARROW LEFT!!
      else if(arrow === "right") {
        let selD = _.cloneDeep(this.selectedDate.get("dateSel")?.value);
        let d1 = _.cloneDeep(selD);
       // if(selD.getMonth() === 9) { NON VA FATTO QUESTO CHECK!

          // selD.setMonth(0);
          // selD.setFullYear(selD.getFullYear() + 1);
          if(this.isLastDayOfMonth(d1)){
            //SIAMO A RIGHT E ALL'ULTIMO GIORNO DEL MESE CASE!
            let d2 = _.cloneDeep(selD);
            d2 = this.addLastDayMonth(d2,3);
            d2.setHours(this.dateEnd.getHours(),this.dateEnd.getMinutes(),this.dateEnd.getSeconds());
            if(d2 >= this.dateEnd){
               //ULTIMA DATA!
              selD = d2;
              this.selectedDate.get("dateSel")?.setValue(selD);
              this.navigateDateLeftMonth = false;
              this.navigateDateRightMonth = false;
              this.navigateDateRightSeason = true;
              this.navigateDateRightYear = false;
              this.navigateDateLeftYear = false;
              this.navigateDateLeftSeason = false;
              this.getMeta(this.selData.get("dataSetSel")?.value.name.dataset_id,"ok");
            }else{
              selD = d2;
              this.selectedDate.get("dateSel")?.setValue(selD);
              this.navigateDateLeftMonth = false;
              this.navigateDateRightMonth = false;
              this.navigateDateRightSeason = false;
              this.navigateDateRightYear = false;
              this.navigateDateLeftYear = false;
              this.navigateDateLeftSeason = false;
              this.getMeta(this.selData.get("dataSetSel")?.value.name.dataset_id,"ok");
            }
          }else{
             //NON SIAMO ALL'ULTIMO GIORNO DEL MESE!!!!!!!
             let d2 = _.cloneDeep(selD);
             d2 = this.addRealMonth(moment(d2), 3).toDate();
             d2.setHours(this.dateEnd.getHours(),this.dateEnd.getMinutes(),this.dateEnd.getSeconds());
             if(d2 >= this.dateEnd){
                //ULTIMA DATA POSSIBILE
                selD = d2;
                this.selectedDate.get("dateSel")?.setValue(selD);
                this.navigateDateLeftMonth = false;
                this.navigateDateRightMonth = false;
                this.navigateDateRightSeason = true;
                this.navigateDateRightYear = false;
                this.navigateDateLeftYear = false;
                this.navigateDateLeftSeason = false;
                this.getMeta(this.selData.get("dataSetSel")?.value.name.dataset_id,"ok");
             }else{
                selD = d2;
                this.selectedDate.get("dateSel")?.setValue(selD);
                this.navigateDateLeftMonth = false;
                this.navigateDateRightMonth = false;
                this.navigateDateRightSeason = false;
                this.navigateDateRightYear = false;
                this.navigateDateLeftYear = false;
                this.navigateDateLeftSeason = false;
                this.getMeta(this.selData.get("dataSetSel")?.value.name.dataset_id,"ok");
              }
          }

        //}
      } //FINE ELSE IF RIGHT
    } // FINE SEASONAL
  } //FINE CHANGE DATE

  dateFilter = (date: Date | null): boolean => {return true;}

  getLayers(idMeta: any, controlDate?: any) {

    //let d = new Date()
    // d.setUTCSeconds
    this.metadata = this.metadata["metadata"];

    console.log("METADATAaaaa ==", this.metadata);
    // d.setUTCSeconds
    // console.log("METADATA 2 ==", this.metadata[0][2]);

    let seconds_epoch = this.metadata[0][2].split(",");

    let seconds_epoch_start = seconds_epoch[0];

    let seconds_epoch_end = seconds_epoch[1];
    console.log("SECONDS EPOCH START ==", seconds_epoch_start);
    console.log("SECONDS EPOCH END ==", seconds_epoch_end);


    let date_start=new Date(0);
    date_start.setUTCSeconds(seconds_epoch_start);
    let date_end=new Date(0);
    date_end.setUTCSeconds(seconds_epoch_end.trim());
    date_start.setHours(date_start.getHours() - 1)
    date_end.setHours(date_end.getHours() - 1)
    console.log("DATE START ==", date_start);
    console.log("DATE END ==", date_end);

    this.dateStart = date_start;
    this.dateEnd = date_end;

    this.dateFilter = (date:Date | null) : boolean =>{
      if(date) {
        if(this.selData.get("dataSetSel")?.value.name.adriaclim_timeperiod === "yearly") {
          //FUNZIONA PERO BOH.........
          return date.getMonth() === this.dateEnd.getMonth() &&
                 date.getDate()  === this.dateEnd.getDate() &&
                 date.getFullYear() >= this.dateStart.getFullYear() &&
                 date.getFullYear() <= this.dateEnd.getFullYear()
        }
        if(this.selData.get("dataSetSel")?.value.name.adriaclim_timeperiod === "monthly") {
          //FUNZIONA PERO BOH.........
          //GESTIRE ULTIMO GIORNO DEL MESE!
          return date.getDate()  === this.dateEnd.getDate() &&
                 date.getFullYear() >= this.dateStart.getFullYear() &&
                 date.getFullYear() <= this.dateEnd.getFullYear()
        }
        if(this.selData.get("dataSetSel")?.value.name.adriaclim_timeperiod === "seasonal") {
          //FUNZIONA PERO BOH.........
          //SAME DAY AND 3 MONTHS DIFFERENCE BETWEEN DAYS!
          return date.getDate()  === this.dateEnd.getDate() &&
                 ((this.dateEnd.getMonth()+1) - (date.getMonth()+1)) % 3 === 0 &&
                 date.getFullYear() >= this.dateStart.getFullYear() &&
                 date.getFullYear() <= this.dateEnd.getFullYear()
        }else{
          return date >= this.dateStart && date <= this.dateEnd;
        }
      }
      else {
        return true;
      }
    }
    // this.myFilter(this.selectedDate.get("dateSel")?.value);


    let time;
    if(controlDate === "ok") {
      let tmp = this.selectedDate.get("dateSel")?.value;
      time = this.formatDate(tmp);
      console.log("TIME OK ==", time);

    }
    else {
      this.selectedDate.get("dateSel")?.setValue(date_end);
      time = this.formatDate(date_end);
      console.log("TIME NO ==", time);
    }

    if(this.selectedDate.get("dateSel")?.value === this.dateEnd) {

      this.navigateDateLeftYear = false;
      this.navigateDateRightYear = true;
      this.navigateDateLeftMonth = false;
      this.navigateDateRightMonth = true;
      this.navigateDateLeftSeason = false;
      this.navigateDateRightSeason = true;
    }

    if(!this.variableGroup.get("variableControl")?.value) {
      this.variableGroup.get("variableControl")?.setValue(this.metadata[0][4]);

    }
    console.log("VARIABILE SELEZIONATA ==", this.variableGroup.get("variableControl")?.value);
    console.log("METADATA 0 4 ==", this.metadata[0][4]);



    // let time = this.formatDate(date_end);
    let layer_name = this.variableGroup.get("variableControl")?.value;

    this.legendLayer_src = this.ERDDAP_URL+"/griddap/"+idMeta+".png?"+layer_name+"%5B("+this.formatDate(time)+")%5D%5B%5D%5B%5D&.legend=Only";

    // console.log("TIME======== ",time);
    //if num_parameters.length > 3, layers3D!!!
    let num_parameters=this.metadata[0][1].split(", ");

    /**
     * CONTROLLO, quando si seleziona l'indicatore di default prendiamo metadata[0][4] invece quando selezioniamo una variabile inseriamo il nome della variabile
     * al posto di metadata[0][4] sia in layer_to_attach che in legendLayer_src
     */
    let layer_to_attach = {
      layer_name: L.tileLayer.wms(
      'http://localhost:8000/test/layers2d',{
      attribution: this.metadata[0][6],
      bgcolor: '0x808080',
      crs: L.CRS.EPSG4326,
      format: 'image/png',
      layers: idMeta +':'+layer_name,
      styles: '',
      time: time,
      transparent: true,
      version: '1.3.0',
      opacity:0.7,
      } as ExtendedWMSOptions)
    };


    //Quando cambia la data cambiare anche la legenda!


    this.datasetLayer = layer_to_attach.layer_name.addTo(this.map);




    // this.httpClient.get('http://localhost:8000/test/layers2d?', {
    //   attribution: this.metadata[0][6],
    //   bgcolor: '0x808080',
    //   crs: L.CRS.EPSG4326,
    //   format: 'image/png',
    //   layers: idMeta +':'+ this.metadata[0][4],
    //   styles: '',
    //   time: time,
    //   transparent: true,
    //   version: '1.3.0',
    //   opacity:0.7,
    // }).subscribe({
    //   next: (res: any) => {
    //     console.log('LAYERS: ', res);
    //     // let layer = L.tileLayer.wms(res.url, res.options);
    //   },
    //   error: (msg: any) => {
    //     console.log('LAYERS ERROR: ', msg);
    //   }

    // });

  }

  landLayers() {

    let overlays = {
      Land: L.tileLayer.wms(
      'http://localhost:8000/test/addOverlays/atm_regional_76a1_c4ac_038a', {
      bgcolor: '0x808080',
      crs: L.CRS.EPSG4326,
      format: 'image/png',
      layers: 'Land',
      styles: '',
      transparent: true,
      version: '1.3.0'} as ExtendedWMSOptions
      ),
    Coastlines: L.tileLayer.wms(
      'http://localhost:8000/test/addOverlays/atm_regional_76a1_c4ac_038a', {
      bgcolor: '0x808080',
      crs: L.CRS.EPSG4326,
      format: 'image/png',
      layers: 'Coastlines',
      styles: '',
      transparent: true,
      version: '1.3.0'} as ExtendedWMSOptions
      ),
    LakesAndRivers: L.tileLayer.wms(
       'http://localhost:8000/test/addOverlays/atm_regional_76a1_c4ac_038a', {
      bgcolor: '0x808080',
      crs: L.CRS.EPSG4326,
      format: 'image/png',
      layers: 'LakesAndRivers',
      styles: '',
      transparent: true,
      version: '1.3.0'} as ExtendedWMSOptions
      ),
    Nations: L.tileLayer.wms(
       'http://localhost:8000/test/addOverlays/atm_regional_76a1_c4ac_038a', {
      bgcolor: '0x808080',
      crs: L.CRS.EPSG4326,
      format: 'image/png',
      layers: 'Nations',
      styles: '',
      transparent: true,
      version: '1.3.0'} as ExtendedWMSOptions
      ),
    States: L.tileLayer.wms(
      'http://localhost:8000/test/addOverlays/atm_regional_76a1_c4ac_038a', {
      bgcolor: '0x808080',
      crs: L.CRS.EPSG4326,
      format: 'image/png',
      layers: 'States',
      styles: '',
      transparent: true,
      version: '1.3.0'} as ExtendedWMSOptions
      )
    };

  let control_layers=L.control.layers().addTo(this.map);
  control_layers.addOverlay(overlays.Land,"Land");
  control_layers.addOverlay(overlays.Coastlines,"Coastlines");
  control_layers.addOverlay(overlays.States,"States");
  control_layers.addOverlay(overlays.Nations,"Nations");
  control_layers.addOverlay(overlays.LakesAndRivers,"LakesAndRivers");

  }

  deleteLayer(idMeta: string) {
    this.legendLayer_src = null;
    if(idMeta !== this.selData.get("dataSetSel")?.value.name.dataset_id) {
      this.selData.reset();

    }

    this.map.removeLayer(this.datasetLayer);
  }

  formatDate(date: any) {
    let d = new Date(date),
        month = '' + (d.getMonth() + 1),
        day = '' + d.getDate(),
        year = d.getFullYear();

    if (month.length < 2)
        month = '0' + month;
    if (day.length < 2)
        day = '0' + day;

    let first_part=[year, month, day].join('-');
    let second_part="T00:00:00Z";
    return first_part+second_part;
  }



  /**
   * TREE
   */

  typesOfShoes: string[] = ['Boots', 'Clogs', 'Loafers', 'Moccasins', 'Sneakers'];
  private _transformer = (node: FoodNode, level: number) => {
    return {
      expandable: !!node.children && node.children.length > 0,
      name: node.name,
      level: level,
    };
  };

  treeControl = new FlatTreeControl<ExampleFlatNode>(
    node => node.level,
    node => node.expandable,
  );

  // treeControl = new NestedTreeControl<FoodNode>((node) => node.children);
  // dataSource = new MatTreeNestedDataSource<FoodNode>();


  treeFlattener = new MatTreeFlattener(
    this._transformer,
    node => node.level,
    node => node.expandable,
    node => node.children,
  );

  dataSource = new MatTreeFlatDataSource(this.treeControl, this.treeFlattener);


  hasChild = (_: number, node: ExampleFlatNode) => node.expandable;
  // hasChild = (_: number, node: FoodNode) =>
  //   !!node.children && node.children.length > 0;


  openTableDialog(idMeta?: string, title?: string) {
    console.log("DATASET ID PER DIALOG ===", this.selData.get("dataSetSel")?.value ? this.selData.get("dataSetSel")?.value.name.dataset_id : idMeta);

    const dialogConfig = new MatDialogConfig();

    dialogConfig.disableClose = true;
    dialogConfig.autoFocus = true;

    dialogConfig.data = {
      success: true,
      datasetId: this.selData.get("dataSetSel")?.value ? this.selData.get("dataSetSel")?.value.name.dataset_id : idMeta,
      datasetName: this.selData.get("dataSetSel")?.value ? this.selData.get("dataSetSel")?.value.name.title : title,
    };


    const dialogRef = this.dialog.open(GeoportalMapDialogComponent, dialogConfig);

    // dialogRef.afterClosed().subscribe(
    //   async data => {
    //     if(data == "ok") {
    //       // this.getAlgoConfig();
    //       dialogConfig.data = {
    //         success: false,
    //         description: "Operation successful"
    //       }
    //       this.dialog.open(AlgorithmConfigurationDialogComponent, dialogConfig);
    //     }
    //     else if(data.id == "exists") {
    //       console.log("DATA =", data);

    //       dialogConfig.data = {
    //         success: false,
    //         description: data.desc
    //       }
    //       this.dialog.open(AlgorithmConfigurationDialogComponent, dialogConfig);
    //     }

    //   }
    // )
  }


}



