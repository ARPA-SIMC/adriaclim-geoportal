import { FlatTreeControl } from '@angular/cdk/tree';
import { HttpClient } from '@angular/common/http';
import { AfterViewInit, Component, ElementRef, OnInit, ViewChild } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import { MatDialog, MatDialogConfig } from '@angular/material/dialog';
import { MatMenuTrigger } from '@angular/material/menu';
import { MAT_SELECT_CONFIG } from '@angular/material/select';
import { MatTreeFlatDataSource, MatTreeFlattener } from '@angular/material/tree';
import * as L from 'leaflet';
import * as _ from 'lodash';
import * as moment from 'moment';
import * as poly from '../../assets/geojson/geojson.json';
import { GeoportalMapDialogComponent } from './geoportal-map-dialog/geoportal-map-dialog.component';

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

interface ExtraParams {
  name: string;
  minValue: number;
  maxValue: number;
  stepSize: number;
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
      // childVisible: false,
      children: [],
    },
    {
      name: 'Indicators',
      // childVisible: true,
      children: [
        {
          name: 'Large scale',
          // childVisible: true,
          children: [
            {name: 'Yearly', children: []},
            {name: 'Monthly', children: []},
            {name: 'Seasonal', children: []}
          ],
        },
        {
          name: 'Pilot scale',
          // childVisible: true,
          children: [
            {name: 'Yearly', children: []},
            {name: 'Monthly', children: []},
            {name: 'Seasonal', children: []}
          ],
        },
        {
          name: 'Local scale',
          // childVisible: true,
          children: [
            {name: 'Yearly', children: []},
            {name: 'Monthly', children: []},
            {name: 'Seasonal', children: []}
          ],
        },
      ],
    },
    {
      name: 'Numerical models',
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
  styleUrls: ['./geoportal-map.component.scss'],
  providers: [
    {
      provide: MAT_SELECT_CONFIG,
      useValue: { overlayPanelClass: 'select-overlay-pane' }
    }
  ]
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

  allPolygons : any[] = [];

  dataInd: any;
  dataAllNodes: any[] = [];

  selData: FormGroup;
  selectedDate: FormGroup;
  variableGroup: FormGroup;
  activeLayersGroup: FormGroup;
  sliderGroup: FormGroup;
  nodeSelected: any;

  metadata: any;
  dateStart: any;
  dateEnd: any;
  extraParam!: ExtraParams;
  isExtraParam!: boolean;
  variableArray: [] = [];
  activeLayersArray: any[] = [];


  pointBoolean = false;

  coordOnClick = {};

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

    this.activeLayersGroup = new FormGroup({
      activeLayersControl: new FormControl(null)
    });

    this.sliderGroup = new FormGroup({
      sliderControl: new FormControl(null)
    });

    // this.getInd();
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
        this.allPolygons.push(pol);
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
    // if(this.pointBoolean === true) {
    //   this.map.on('click', this.onMapClick.bind(this));

    // }

    // ASSEGNO DEI VALORI E GENERO UN POLIGONO


  }

  // addPolygons() {

  pointSelect() {
    // if(this.pointBoolean === false) {
      // this.pointBoolean = true;
      this.map.on('click', this.onMapClick.bind(this));
    // }

    // this.initMap();
  }

  polygonSelect() {
    this.map.on('click', this.onPolygonClick.bind(this));
  }

  // }
  onPolygonClick = (e: L.LeafletMouseEvent) => {
    this.map.off('click');
    if(this.activeLayersArray.length === 0){
        //hai cliccato il bottone e un punto ma non ci sono layer attivi
        //WARNING!

    }else{
      console.log("EVENT POLYGON =", e);
      this.allPolygons.forEach((pol:any)=>{
        if(pol.getBounds().contains(e.latlng)){
          console.log("The polygon is rullo di tamburi",pol);
        }
      });
      var label = e.target.options.label;
      var content = e.target.options.popup;
      var otherStuff = e.target.options.otherStuff;
      alert("Clicked on polygon with label:" +label +" and content:" +content +". Also otherStuff set to:" +otherStuff);
    }
  }

  // metodo richiamato al click sulla mappa
  onMapClick = (e: L.LeafletMouseEvent) => {
    // this.pointBoolean = false;
    this.map.off('click');

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
    console.log("LAT========",e.latlng.lat);
    console.log("LONG===========",e.latlng.lng);
    this.coordOnClick = {
      lat: e.latlng.lat,
      lng: e.latlng.lng
    }
    console.log("COORDINATE ON CLICK =", this.coordOnClick);
    this.openGraphDialog();
    // this.pointBoolean = false;
    // METODO 2
    const marker = L.marker(e.latlng, {
      icon: L.icon({
          iconSize: [25, 41],
          iconAnchor: [13, 41],
          iconUrl: 'marker-icon.png',
      })
    });
    marker.on('click', this.onMarkerClick.bind(this));
    // console.log("MARKER =", marker);

    // marker.addTo(this.map);
    this.markers.push(marker);

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

          //riempiamo tree con tutti i nodi
          if (node.adriaclim_dataset === "indicator"){
            let indicatori = TREE_DATA.filter((indicators: any) => indicators.name === "Indicators")[0]
            console.log("INDICATORI =", indicatori);

            let scale = indicatori.children?.filter((sca: any) => sca.name.toLowerCase().includes(node.adriaclim_scale.toLowerCase()))[0];
            let time = scale?.children?.filter((time: any) => time.name.toLowerCase().includes(node.adriaclim_timeperiod.toLowerCase()))[0];
            if(time?.children?.findIndex(elInd => elInd.name === node.title) === -1) {
              time?.children?.push({
                name: node
              });
              time?.children?.sort((o1:any, o2:any) => {
                if (o1.name.title > o2.name.title) {
                  return 1;
                }
                if (o1.name.title < o2.name.title) {
                  return -1;
                }
                return 0;
              })
              // time.childVisible = true;
            }
          }
          else if (node.adriaclim_dataset === "model"){
            let modelli = TREE_DATA.filter((models: any) => models.name === "Numerical models")[0]
            if(modelli?.children?.findIndex(elModel => elModel.name === node.title) === -1){
              modelli?.children?.push({
                name: node
              });
              modelli?.children?.sort((o1: any, o2: any) => {
                if (o1.name.title > o2.name.title) {
                  return 1;
                }
                if (o1.name.title < o2.name.title) {
                  return -1;
                }
                return 0;
              })
            }
          }
          else if (node.adriaclim_dataset === "observation"){
            let observation = TREE_DATA.filter((obs: any) => obs.name === "Observations")[0]
            console.log("OBSERVATION =", observation);

            if(observation?.children?.findIndex(elObs => elObs.name === node.title) === -1){
              observation?.children?.push({
                name: node
              });
              observation?.children?.sort((o1: any, o2: any) => {


                if (o1.name.title > o2.name.title) {
                  return 1;
                }
                if (o1.name.title < o2.name.title) {
                  return -1;
                }
                return 0;
              })

            }

          }




          // let observations = TREE_DATA.filter((indicators: any) => indicators.name === "Indicators")[0]

            this.dataAllNodes.push(
              {name: node}
            );

          });


          this.dataAllNodesTree.data = TREE_DATA;


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
    this.httpClient.post('http://localhost:8000/test/ind', {
    }).subscribe({
      next: (res: any) => {

        this.dataInd = res.ind;

        this.dataInd.forEach((ind: any) => {
          let indicatori = TREE_DATA.filter((node: any) => node.name === "Indicators")[0]
          let scale = indicatori.children?.filter((sca: any) => sca.name.toLowerCase().includes(ind.adriaclim_scale.toLowerCase()))[0];
          let time = scale?.children?.filter((time: any) => time.name.toLowerCase().includes(ind.adriaclim_timeperiod.toLowerCase()))[0];
          if(time?.children?.findIndex(title => title.name === ind.title) === -1) {
            time?.children?.push({
              name: ind
            });
            // time.childVisible = true;
          }

          });

          this.dataSource.data = TREE_DATA;
      },
      error: (msg: any) => {
        console.log('IND ERROR: ', msg);
      }

    });

  }

  addToActiveLayers(node: any) {
    // this.selData.get("dataSetSel")?.value
    // if(this.selData.get("dataSetSel")?.value) {
    this.activeLayersArray.push(node);
    // this.activeLayersGroup.get("activeLayersControl")?.setValue(node);
    this.selData.get("dataSetSel")?.setValue(node);
    // console.log("COSA C'E' IN STO SELDATA ==", this.selData.get("dataSetSel")?.value);

    console.log("Added layer====", this.activeLayersArray);
    // }
  }

  selActiveLayer(event: any) {
    console.log("SELECTED LAYER =", event.value);
    // this.selData.get("dataSetSel")?.setValue();
    console.log("COSA C'E' IN STO SELDATA ==", this.selData.get("dataSetSel")?.value);

    let metaId: any;
    if(this.selData.get("dataSetSel")?.value.name.dataset_id) {
      metaId = this.selData.get("dataSetSel")?.value.name.dataset_id;

    }

    else if(this.selData.get("dataSetSel")?.value.name.id) {
      metaId = this.selData.get("dataSetSel")?.value.name.id;
    }
    // if(event.value.dataset_id) {
    //   /**
    //   *  controllare anche qui!
    //   */

    //   // console.log("sono in event.value.dataset_id");
    //   metaId = event.value.dataset_id;
    //   // console.log("DATASET_ID====",metaId);
    //   // console.log("TITLE=====",event.value.title);
    //   // console.log("TIME START======",event.value.time_start);
    //   // console.log("TIME END======",event.value.time_end);

    // }
    // else if(event.value.id) {
    //   /**
    //    * constrollare qui con console.log
    //    */
    //   // console.log("sono in event.value.id");
    //   metaId = event.value.id;
    //   // console.log("DATASET_ID====",metaId);
    //   // console.log("TITLE=====",event.value.title);

    // }
    console.log("METADATA ID =", metaId);

    this.getSelectedNode(event.value);
    this.getMeta(metaId);
  }

  getMeta(idMeta: any, controlDate?: any, controlExtra?: any) {


    if(this.legendLayer_src) {
      this.deleteLayer(idMeta);

    }
    this.httpClient.post('http://localhost:8000/test/metadata', {
      idMeta: idMeta
    }).subscribe({
      next: (res: any) => {
        // console.log('METADATA: ', res);
        this.metadata = res;
        console.log("METADATA =", this.metadata);

        if(controlDate === "ok") {

          this.getLayers(idMeta, controlDate, controlExtra);
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

    if(node.name) {
      this.variableArray = node.name.variable_names.split(" ");
    }
    else if(node.variable_names) {
      this.variableArray = node.variable_names.split(" ");
    }
    this.variableGroup.get("variableControl")?.setValue(this.variableArray[this.variableArray.length - 1]);

  }


  lastday(y:any,m:any){
    // console.log("LAST DAY ==", new Date(y, m + 1, 0).getDate());

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
    let metaId: any;
    if(this.selData.get("dataSetSel")?.value.name.dataset_id) {
      metaId = this.selData.get("dataSetSel")?.value.name.dataset_id;

    }

    else if(this.selData.get("dataSetSel")?.value.name.id) {
      metaId = this.selData.get("dataSetSel")?.value.name.id;
    }



    if(arrow === "leftAll") {
      this.selectedDate.get("dateSel")?.setValue(this.dateStart);
      //leftAll is clicked so we disable left button and enable the right ones
      this.navigateDateLeftYear = true;
      this.navigateDateRightYear = false;
      this.navigateDateRightMonth = false;
      this.navigateDateRightSeason = false;
      this.navigateDateLeftMonth = false;
      this.navigateDateLeftSeason = false;
      this.getMeta(metaId,"ok");
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
      this.getMeta(metaId,"ok");
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
          this.getMeta(metaId,"ok");
        }else{
          selD.setFullYear(selD.getFullYear() - 1);
          this.selectedDate.get("dateSel")?.setValue(selD);
          this.navigateDateLeftYear = false;
          this.navigateDateRightYear = false;
          this.navigateDateRightMonth = false;
          this.navigateDateRightSeason = false;
          this.getMeta(metaId,"ok");
        }
      }
      else if(arrow === "right") {
        let selD = _.cloneDeep(this.selectedDate.get("dateSel")?.value);
        if((selD.getFullYear() + 1) === this.dateEnd.getFullYear()){
          selD.setFullYear(selD.getFullYear() + 1);
          this.selectedDate.get("dateSel")?.setValue(selD);
          this.navigateDateRightYear = true;
          this.navigateDateLeftYear = false;
          this.getMeta(metaId,"ok");
        }else{
          selD.setFullYear(selD.getFullYear() + 1);
          this.selectedDate.get("dateSel")?.setValue(selD);
          this.navigateDateRightYear = false;
          this.navigateDateLeftYear = false;
          this.getMeta(metaId,"ok");
        }

      }
    }
    else if(this.selData.get("dataSetSel")?.value.name.adriaclim_timeperiod === "monthly") {
      if(arrow === "left") {
        let selD = _.cloneDeep(this.selectedDate.get("dateSel")?.value);
        // console.log(selD);
        let d1 = _.cloneDeep(selD);
        if(this.isLastDayOfMonth(d1)){
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
              this.getMeta(metaId,"ok");
          }else{
            selD = d2;
            this.selectedDate.get("dateSel")?.setValue(selD);
            this.navigateDateLeftMonth = false;
            this.navigateDateRightMonth = false;
            this.navigateDateRightSeason = false;
            this.navigateDateRightYear = false;
            this.navigateDateLeftYear = false;
            this.navigateDateLeftSeason = false;
            this.getMeta(metaId,"ok");
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
            this.getMeta(metaId,"ok");
          }else{
            selD = d2;
            this.selectedDate.get("dateSel")?.setValue(selD);
            this.navigateDateLeftMonth = false;
            this.navigateDateRightMonth = false;
            this.navigateDateRightSeason = false;
            this.navigateDateRightYear = false;
            this.navigateDateLeftYear = false;
            this.navigateDateLeftSeason = false;
            this.getMeta(metaId,"ok");
          }
        }
      }
      else if(arrow === "right") {

        let selD = _.cloneDeep(this.selectedDate.get("dateSel")?.value);
        let d1 = _.cloneDeep(selD);
        if(this.isLastDayOfMonth(d1)){
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
              this.getMeta(metaId,"ok");
          }else{
            selD = d2;
            this.selectedDate.get("dateSel")?.setValue(selD);
            this.navigateDateLeftMonth = false;
            this.navigateDateLeftYear = false;
            this.navigateDateLeftSeason = false;
            this.navigateDateRightMonth = false;
            this.navigateDateRightSeason = false;
            this.navigateDateRightYear = false;
            this.getMeta(metaId,"ok");
          }


        } else{
          //NON SIAMO ALL'ULTIMO GIORNO DEL MESE!
          let d2 = _.cloneDeep(selD);
          d2 = this.addRealMonth(moment(d2), 1).toDate();
          d2.setHours(this.dateEnd.getHours(),this.dateEnd.getMinutes(),this.dateEnd.getSeconds());
          if(d2.toString() === this.dateEnd.toString()){
            //ULTIMA DATA!
            selD = d2;
            this.selectedDate.get("dateSel")?.setValue(selD);
            this.navigateDateLeftMonth = false;
            this.navigateDateRightMonth = true;
            this.navigateDateRightSeason = false;
            this.navigateDateRightYear = false;
            this.navigateDateLeftYear = false;
            this.navigateDateLeftSeason = false;
            this.getMeta(metaId,"ok");
          }else{
            selD = d2;
            this.selectedDate.get("dateSel")?.setValue(selD);
            this.navigateDateLeftMonth = false;
            this.navigateDateLeftYear = false;
            this.navigateDateLeftSeason = false;
            this.navigateDateRightMonth = false;
            this.navigateDateRightSeason = false;
            this.navigateDateRightYear = false;
            this.getMeta(metaId,"ok");
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
              this.getMeta(metaId,"ok");

            }else{
              selD = d2;
              this.selectedDate.get("dateSel")?.setValue(selD);
              this.navigateDateLeftMonth = false;
              this.navigateDateLeftYear = false;
              this.navigateDateLeftSeason = false;
              this.navigateDateRightMonth = false;
              this.navigateDateRightSeason = false;
              this.navigateDateRightYear = false;
              this.getMeta(metaId,"ok");
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
              this.getMeta(metaId,"ok");
            }else{
              selD = d2;
              this.selectedDate.get("dateSel")?.setValue(selD);
              this.navigateDateLeftMonth = false;
              this.navigateDateRightMonth = false;
              this.navigateDateRightSeason = false;
              this.navigateDateRightYear = false;
              this.navigateDateLeftYear = false;
              this.navigateDateLeftSeason = false;
              this.getMeta(metaId,"ok");
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
              this.getMeta(metaId, "ok");
            }else{
              selD = d2;
              this.selectedDate.get("dateSel")?.setValue(selD);
              this.navigateDateLeftMonth = false;
              this.navigateDateRightMonth = false;
              this.navigateDateRightSeason = false;
              this.navigateDateRightYear = false;
              this.navigateDateLeftYear = false;
              this.navigateDateLeftSeason = false;
              this.getMeta(metaId,"ok");
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
                this.getMeta(metaId,"ok");
             }else{
                selD = d2;
                this.selectedDate.get("dateSel")?.setValue(selD);
                this.navigateDateLeftMonth = false;
                this.navigateDateRightMonth = false;
                this.navigateDateRightSeason = false;
                this.navigateDateRightYear = false;
                this.navigateDateLeftYear = false;
                this.navigateDateLeftSeason = false;
                this.getMeta(metaId,"ok");
              }
          }

        //}
      } //FINE ELSE IF RIGHT
    } // FINE SEASONAL
    if(this.dateStart?.toString() === this.dateEnd?.toString()) {
      this.navigateDateLeftYear = true;
      this.navigateDateRightYear = true;
      this.navigateDateLeftMonth = true;
      this.navigateDateRightMonth = true;
      this.navigateDateLeftSeason = true;
      this.navigateDateRightSeason = true;
    }
  } //FINE CHANGE DATE

  dateFilter = (date: Date | null): boolean => {return true;}

  getLayers(idMeta: any, controlDate?: any, controlExtra?: any) {

    //let d = new Date()
    // d.setUTCSeconds
    this.metadata = this.metadata["metadata"];

    // console.log("METADATAaaaa ==", this.metadata);
    // d.setUTCSeconds
    // console.log("METADATA 2 ==", this.metadata[0][2]);

    let seconds_epoch = this.metadata[0][2].split(",");

    let seconds_epoch_start = seconds_epoch[0];

    let seconds_epoch_end = seconds_epoch[1];

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
    // console.log("SELECTED DATASET: ", this.selData.get('dataSetSel')?.value);

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
          let d1 = _.cloneDeep(this.dateEnd);
          if(this.isLastDayOfMonth(d1)){
            //ULTIMO GIORNO DEL MESE CASISTICA
            //mi prendi quelli di tutti i mesi precedenti e dell'ultimo giorno
            let d2 = _.cloneDeep(date);
            if(d2<=this.dateEnd && d2>=this.dateStart && this.isLastDayOfMonth(d2)){
              return true;
            }else{
              return false;
            }
          }else{
              return date.getDate()  === this.dateEnd.getDate() &&
                    date.getFullYear() >= this.dateStart.getFullYear() &&
                    date.getFullYear() <= this.dateEnd.getFullYear()
            }
        }
        if(this.selData.get("dataSetSel")?.value.name.adriaclim_timeperiod === "seasonal") {
          //FUNZIONA PERO BOH.........
          //SAME DAY AND 3 MONTHS DIFFERENCE BETWEEN DAYS!
          //GESTIRE ULTIMO GIORNO DEL MESE
          let d1 = _.cloneDeep(this.dateEnd);
          if(this.isLastDayOfMonth(d1)){
            //ULTIMO GIORNO DEL MESE CASISTICA
            //mi prendi quelli di tutte le stagioni precedenti e dell'ultimo giorno
            let d2 = _.cloneDeep(date);
            if(d2<=this.dateEnd && d2>=this.dateStart && ((this.dateEnd.getMonth()+1) - (d2.getMonth()+1)) % 3 === 0 && this.isLastDayOfMonth(d2)){
              return true;
            }else{
              return false;
            }
          }else{
            return date.getDate()  === this.dateEnd.getDate() &&
                  ((this.dateEnd.getMonth()+1) - (date.getMonth()+1)) % 3 === 0 &&
                  date.getFullYear() >= this.dateStart.getFullYear() &&
                  date.getFullYear() <= this.dateEnd.getFullYear();
          }

        }else{
          //SE NON è SEASONAL,MONTHLY O YEARLY PRENDE TUTTE LE DATE COMPRESE!
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

    }
    else {
      this.selectedDate.get("dateSel")?.setValue(date_end);
      time = this.formatDate(date_end);
    }

    if(this.selectedDate.get("dateSel")?.value === this.dateEnd) {

      this.navigateDateLeftYear = false;
      this.navigateDateRightYear = true;
      this.navigateDateLeftMonth = false;
      this.navigateDateRightMonth = true;
      this.navigateDateLeftSeason = false;
      this.navigateDateRightSeason = true;
    }

    //se non è settata setta a this.metadata[0][4], se viene cambiata prendila da variable group
    //se cambio layer, cambiano le variabili quindi settare di nuovo a this.metadata
    if(!this.variableGroup.get("variableControl")?.value) {
      this.variableGroup.get("variableControl")?.setValue(this.metadata[0][4]);

    }



    let layer_name = this.variableGroup.get("variableControl")?.value;

    this.legendLayer_src = this.ERDDAP_URL+"/griddap/"+idMeta+".png?"+layer_name+"%5B("+this.formatDate(time)+")%5D%5B%5D%5B%5D&.legend=Only";


    //if num_parameters.length > 3, layers3D!!!
    let num_parameters=this.metadata[0][1].split(", ");
    let layer_to_attach : any;



    if(num_parameters.length <= 3){
      this.isExtraParam = false;
      //siamo nel caso di layers 2D!!!
      layer_to_attach = {
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

      this.legendLayer_src = this.ERDDAP_URL+"/griddap/"+idMeta+".png?"+layer_name+"%5B("+this.formatDate(time)+")%5D%5B%5D%5B%5D&.legend=Only";

    }else{

      //siamo nel caso di layers 3D!!
      //di default gli assegniamo il minimo valore!
      let min_max_value=this.metadata[0][0].split(",");
      let name = num_parameters[1];
      let min = Number(min_max_value[0]);
      let max = Number(min_max_value[1]);
      let step = Number(this.metadata[0][5].split("=")[1]);

      //se non c'è ci sono questi due if, se c'è hai sempre
      if(name === "depth"){
        // this.extraParam.name = "elevation";
        this.extraParam = {
          name: "Elevation",
          minValue: - max,
          maxValue: - min,
          stepSize: step,
        };

      }
      else {
        this.extraParam = {
          name: 'Dim_' + name,
          minValue: min,
          maxValue: max,
          stepSize: step,
        };
      }
      if(controlExtra){
        this.sliderGroup.get('sliderControl')?.setValue(controlExtra);

        layer_to_attach={
          layer_name: L.tileLayer.wms(
        'http://localhost:8000/test/layers3d/'+this.extraParam.name,{
          attribution: this.metadata[0][6],
          bgcolor: '0x808080',
          crs: L.CRS.EPSG4326,
          format: 'image/png',
          layers: idMeta+':'+layer_name,
          styles: '',
          time: time,
          [this.extraParam.name]: controlExtra,
          transparent: true,
          version: '1.3.0',
          opacity:0.7,
          } as ExtendedWMSOptions)
        };

        this.isExtraParam = true;
        if(name === "depth"){
          this.legendLayer_src = this.ERDDAP_URL+"/griddap/"+idMeta+".png?"+layer_name+"%5B("+this.formatDate(time)+")%5D%5B("+(-controlExtra)+")%5D%5B%5D%5B%5D&.legend=Only";
        }else{
          this.legendLayer_src = this.ERDDAP_URL+"/griddap/"+idMeta+".png?"+layer_name+"%5B("+this.formatDate(time)+")%5D%5B("+(controlExtra)+")%5D%5B%5D%5B%5D&.legend=Only";
        }
      }
      else {
        if(name === "depth"){
          this.sliderGroup.get('sliderControl')?.setValue(this.extraParam.maxValue);
        }
        else {
          this.sliderGroup.get('sliderControl')?.setValue(this.extraParam.minValue);
        }


        layer_to_attach={
          layer_name: L.tileLayer.wms(
        'http://localhost:8000/test/layers3d/'+this.extraParam.name,{
          attribution: this.metadata[0][6],
          bgcolor: '0x808080',
          crs: L.CRS.EPSG4326,
          format: 'image/png',
          layers: idMeta+':'+layer_name,
          styles: '',
          time: time,
          [this.extraParam.name]: this.sliderGroup.get('sliderControl')?.value,
          transparent: true,
          version: '1.3.0',
          opacity:0.7,
          } as ExtendedWMSOptions)
        };

        this.isExtraParam = true;
        this.legendLayer_src = this.ERDDAP_URL+"/griddap/"+idMeta+".png?"+layer_name+"%5B("+this.formatDate(time)+")%5D%5B("+this.sliderGroup.get('sliderControl')?.value+")%5D%5B%5D%5B%5D&.legend=Only";

      }


    }

    this.datasetLayer = layer_to_attach.layer_name.addTo(this.map);


  }

  sliderControl(event: any) {
    let valueCustom = event.target.value;
    let metaId: any;
    if(this.selData.get("dataSetSel")?.value.name.dataset_id) {
      metaId = this.selData.get("dataSetSel")?.value.name.dataset_id;
    }
    else if(this.selData.get("dataSetSel")?.value.name.id) {
      metaId = this.selData.get("dataSetSel")?.value.name.id;
    }
    this.getMeta(metaId, "ok", valueCustom);
  }

  formatLabel(value: number): string {
    if (value >= 1000) {
      return Math.round(value / 1000) + 'k';
    }

    return `${value}`;
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

  deleteLayer(idMeta?: string) {
    // console.log("SELECTED DATASET: ", this.selData.get('dataSetSel')?.value);
    // console.log("ID META SOTTO SELECTED DATASET======",idMeta);
    this.legendLayer_src = null;
    let metaId: any;
    if(idMeta) {
      metaId = idMeta;
    }
    else {
      if(this.selData.get("dataSetSel")?.value.name.dataset_id) {
        metaId = this.selData.get("dataSetSel")?.value.name.dataset_id;
      }
      else if(this.selData.get("dataSetSel")?.value.name.id) {
        metaId = this.selData.get("dataSetSel")?.value.name.id;
      }
    }
    // if(this.selData.get('dataSetSel')?.value.name){
    //   if(idMeta !== this.selData.get("dataSetSel")?.value.name.dataset_id) {
    //     console.log("RESET DATASET NAME");

    //     this.selData.reset();

    //   }

    // }

    // else if(idMeta !== this.selData.get("dataSetSel")?.value.dataset_id) {
    //   console.log("RESET DATASET NO NAME");

    //   this.selData.reset();
    // }


    this.map.removeLayer(this.datasetLayer);

  }

  deleteElActiveLayers() {

    let metaId: any;
    if(this.selData.get("dataSetSel")?.value.name.dataset_id) {
      metaId = this.selData.get("dataSetSel")?.value.name.dataset_id;
    }
    else if(this.selData.get("dataSetSel")?.value.name.id) {
      metaId = this.selData.get("dataSetSel")?.value.name.id;
    }

    this.activeLayersArray.forEach((layer:any, i: number)=>{
      if(layer.name.dataset_id === metaId){
        //rimuovi array nel caso di layer da lista dataset
        this.activeLayersArray.splice(i,1);
      }else if(layer.name.id === metaId){
        //rimuovi array nel caso di layer da full list
        this.activeLayersArray.splice(i,1);
      }
    });
    if(this.activeLayersArray.length >=1 ){
      this.selData.get("dataSetSel")?.setValue(this.activeLayersArray[this.activeLayersArray.length-1]);
      // if(this.selData.get("dataSetSel")?.value) {
      //   this.getMeta();
      // }
      if(this.selData.get("dataSetSel")?.value.name.dataset_id) {
        metaId = this.selData.get("dataSetSel")?.value.name.dataset_id;
      }
      else if(this.selData.get("dataSetSel")?.value.name.id) {
        metaId = this.selData.get("dataSetSel")?.value.name.id;
      }
      this.getSelectedNode(this.selData.get("dataSetSel")?.value);
      this.getMeta(metaId);
    }
    else {
      this.selData.reset();
      this.variableArray = [];
    }
    console.log("SEL DATA", this.selData.get("dataSetSel")?.value);


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
  dataAllNodesTree = new MatTreeFlatDataSource(this.treeControl, this.treeFlattener);


  hasChild = (_: number, node: ExampleFlatNode) => node.expandable;
  // hasChild = (_: number, node: FoodNode) =>
  //   !!node.children && node.children.length > 0;


  openTableDialog(idMeta?: string, title?: string) {
    let dataId: any;
    if(!idMeta){
      if(this.selData.get("dataSetSel")?.value.name.dataset_id) {
        dataId = this.selData.get("dataSetSel")?.value.name.dataset_id;
      }
      else if(this.selData.get("dataSetSel")?.value.name.id) {
        dataId = this.selData.get("dataSetSel")?.value.name.id;
      }
    }


    const dialogConfig = new MatDialogConfig();

    dialogConfig.disableClose = true;
    dialogConfig.autoFocus = true;

    dialogConfig.data = {
      success: true,
      datasetId: this.selData.get("dataSetSel")?.value ? dataId : idMeta,
      datasetName: this.selData.get("dataSetSel")?.value ? this.selData.get("dataSetSel")?.value.name.title : title,
    };


    const dialogRef = this.dialog.open(GeoportalMapDialogComponent, dialogConfig);

  }

  openGraphDialog() {
    const dialogConfig = new MatDialogConfig();
    dialogConfig.disableClose = true;
    dialogConfig.autoFocus = true;

    let dataId: any;
    if(this.selData.get("dataSetSel")?.value) {
      console.log("DATASET SELEZIONATO", this.selData.get("dataSetSel")?.value.name);

      // CASO DATASET SELEZIONATO
      let title = this.selData.get("dataSetSel")?.value.name.title;

      if(this.selData.get("dataSetSel")?.value.name.dataset_id) {
        dataId = this.selData.get("dataSetSel")?.value.name.dataset_id;
      }
      else if(this.selData.get("dataSetSel")?.value.name.id) {
        dataId = this.selData.get("dataSetSel")?.value.name.id;

      }

      dialogConfig.data = {
        success: true,
        datasetId: dataId,
        datasetName: title,
        dataset: this.selData.get("dataSetSel")?.value.name,
        latlng: this.coordOnClick,
        dateStart: this.dateStart,
        dateEnd: this.dateEnd,
        variable: this.variableGroup.get("variableControl")?.value,
        arrayVariable: this.variableArray,
        range: this.sliderGroup.get("sliderControl")?.value,
        openGraph: true,
      };

    }
    else {
      //CASO DATASET NON SELEZIONATO
      dialogConfig.data = {
        success: true,
        description: "Select a dataset to visualize the graph",
        openGraph: true,
      };
    }

    const dialogRef = this.dialog.open(GeoportalMapDialogComponent, dialogConfig);

  }
}

