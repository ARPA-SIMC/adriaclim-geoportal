import { Options } from '@angular-slider/ngx-slider';
import { SelectionModel } from '@angular/cdk/collections';
import { FlatTreeControl } from '@angular/cdk/tree';
import { HttpClient } from '@angular/common/http';
import { AfterViewInit, Component, ElementRef, HostListener, OnChanges, OnInit, SimpleChanges, ViewChild } from '@angular/core';
import { FormArray, FormBuilder, FormControl, FormGroup } from '@angular/forms';
import { MatDialog, MatDialogConfig } from '@angular/material/dialog';
import { MatMenuTrigger } from '@angular/material/menu';
import { MAT_SELECT_CONFIG } from '@angular/material/select';
import { MatTreeFlatDataSource, MatTreeFlattener } from '@angular/material/tree';
import * as L from 'leaflet';
import * as _ from 'lodash';
import * as moment from 'moment';
import { debounceTime, distinctUntilChanged, map, startWith } from 'rxjs';
import * as poly from '../../assets/geojson/geojson.json';
import { GeoportalMapDialogComponent } from '../geoportal-map/geoportal-map-dialog/geoportal-map-dialog.component';
import { HttpService } from '../services/http.service';
import { environmentDev, environmentProd, environmentDevProd } from 'src/assets/environments';
import { GeoportalColorDialogComponent } from '../geoportal-map/geoportal-color-dialog/geoportal-color-dialog.component';
import { GeoportalCompareDialogComponent } from '../geoportal-map/geoportal-compare-dialog/geoportal-compare-dialog.component';
import { SelectCoordsDialogComponent } from '../select-coords-dialog/select-coords-dialog.component';
import * as bootstrap from 'bootstrap';
import { MatSnackBar, MatSnackBarHorizontalPosition, MatSnackBarVerticalPosition } from '@angular/material/snack-bar';
import { ExampleFlatNode, ExtendedWMSOptions, ExtraParams, FoodNode, circleCoords } from '../interfaces/geoportal-map-int';
import { titleCaseWord } from '../common-functions/functions';

/**
 * Food data with nested structure.
 * Each node has a name and an optional list of children.
 */
const TREE_DATA: FoodNode[] = [
  //i children di tutti sono riempiti in maniera dinamica con il metodo getAllNodes
  {
    name: 'Observations',
    // childVisible: false,
    children: [],
  },
  {
    name: 'Indicators',
    // childVisible: true,
    children: [

      // {
      //   name: 'Large scale',
      //   // childVisible: true,
      //   children: [
      //     { name: 'Yearly', children: [] },
      //     { name: 'Monthly', children: [] },
      //     { name: 'Seasonal', children: [] }
      //   ],
      // },
      // {
      //   name: 'Pilot scale',
      //   // childVisible: true,
      //   children: [
      //     { name: 'Yearly', children: [] },
      //     { name: 'Monthly', children: [] },
      //     { name: 'Seasonal', children: [] }
      //   ],
      // },
      // {
      //   name: 'Local scale',
      //   // childVisible: true,
      //   children: [
      //     { name: 'Yearly', children: [] },
      //     { name: 'Monthly', children: [] },
      //     { name: 'Seasonal', children: [] }
      //   ],
      // },
    ],
  },
  {
    name: 'Numerical models',
    children: [],
  },
];

@Component({
  selector: 'app-geoportal-map-new',
  templateUrl: './geoportal-map-new.component.html',
  styleUrls: ['./geoportal-map-new.component.scss'],
  providers: [
    {
      provide: MAT_SELECT_CONFIG,
      useValue: { overlayPanelClass: 'select-overlay-pane' }
    }
  ]
})
export class GeoportalMapNewComponent implements OnInit, AfterViewInit {

  toppingList: string[] = ['Extra cheese', 'Mushroom', 'Onion', 'Pepperoni', 'Sausage', 'Tomato'];

  isExpandedFirst = false;
  isExpandedSecond = false;
  isExpandedThird = false;
  isExpandedFourth = false;

  resAllNodes: any;

  categoryDatasets: any[] = [];
  scaleDatasets: any[] = [];
  timeperiodDatasets: any[] = [];
  menuDatasets: any[] = [];

  indicators: any[] = [];
  models: any[] = [];
  observations: any[] = [];
  reanallysis: any[] = [];

  firstList: any[] = ["NameOne", "NameTwo", "NameThree"];
  secondList: any[] = ["NameOne", "NameTwo", "NameThree"];
  thirdList: any[] = ["NameOne", "NameTwo", "NameThree"];

  mod = false;
  isMouseIdle = false;
  timer: any = 10;
  @ViewChild('modProva') modProva: any;
  showModalBox = false;
  display = 'none';

  panelOpenState = false;

  @ViewChild('map') mapContainer!: ElementRef;
  map!: L.Map;
  // centroid: L.LatLngExpression = [41.9027835, 12.4963655]; // Roma
  center: L.LatLngExpression = [42.744388161339, 12.0809380292276]; // Centro Italia
  zoom = 6;

  markersLayer: any = L.layerGroup(); // crea un nuovo layerGroup vuoto
  rettangoliLayer: any = L.layerGroup(); // crea un nuovo layerGroup vuoto
  // markersLayer: any = L.markerClusterGroup(); // crea un nuovo layerGroup vuoto

  apiUrl = environmentDev;

  compliantErrorErddap = "";
  showAlert = false;

  markers: L.Marker[] = [];

  polygon = poly;

  allPolygons: any[] = [];

  dataInd: any;
  dataAllNodes: any[] = [];

  selData: FormGroup;
  selectedDate: FormGroup;
  variableGroup: FormGroup;
  activeLayersGroup: FormGroup;
  sliderGroup: FormGroup;
  nodeSelected: any;
  valueMin: any;
  valueMid: any;
  valueMax: any;
  allDataVectorial: any;

  markerPoint!: L.Marker;

  clickPointOnOff = false;
  clickPolygonOnOff = false;
  confronto = false;
  compare = false;

  metadata: any;
  dateStart: any;
  dateEnd: any;
  extraParam!: ExtraParams;
  extraParamExport!: ExtraParams;
  isExtraParam!: boolean;
  variableArray: any[] = [];
  activeLayersArray: any[] = [];
  legendNoWms: any;
  style: any;
  markerToAdd: any;
  circleMarkerArray: any[] = [];
  rectangleArray: any[] = [];
  circleCoords: circleCoords[] = [];

  valueMinColor: any = "#f44336";
  valueMinMidColor: any = "#e91e63";
  valueMidColor: any = "#9c27b0";
  valueMidMaxColor: any = "#673ab7";
  valueMaxColor: any = "#3f51b5";

  valueMinColorDefault: any = "#f44336";
  valueMinMidColorDefault: any = "#e91e63";
  valueMidColorDefault: any = "#9c27b0";
  valueMidMaxColorDefault: any = "#673ab7";
  valueMaxColorDefault: any = "#3f51b5";

  compareObj: any = {};

  layer_to_attach: any;

  value: any;
  valueCustom: any;
  options: Options = {
    floor: 0,
    ceil: 100,
    step: 1,
  };

  isIndicator !: boolean;

  pointBoolean = false;

  coordOnClick = {};
  filteredData: any;

  ERDDAP_URL = "https://erddap-adriaclim.cmcc-opa.eu/erddap";
  legendLayer_src: any;
  datasetLayer: any;

  navigateDateLeftYear = false;
  navigateDateRightYear = true;
  navigateDateLeftMonth = false;
  navigateDateRightMonth = true;
  navigateDateLeftSeason = false;
  navigateDateRightSeason = true;

  datasetCompare: any = null;

  selectCoords = false;

  formMenuDatasets: FormGroup;
  formMenuCheckbox: FormGroup;

  constructor(private httpClient: HttpClient, private dialog: MatDialog, private httpService: HttpService, private _snackBar: MatSnackBar, private fb: FormBuilder) {

    this.selData = new FormGroup({
      dataSetSel: new FormControl(),
      searchText: new FormControl(),
      searchTextDataset: new FormControl(),
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

    this.formMenuDatasets = this.fb.group({
      category: null,
      scale: null,
      timeperiod: null,
      dataset: null
    });

    this.formMenuCheckbox = this.fb.group({
      toppings: null,
    });
    // this.getInd();

    this.getAllNodes();

    // this.dataSource.data = TREE_DATA;

    this.filteredData = this.dataAllNodesTree.data;
    // console.log("this.filteredData", this.filteredData);
    // if(this.selData.get('searchTextDataset')?.value) {
    this.selData.get('searchTextDataset')?.valueChanges.pipe(
      startWith(''),
      debounceTime(500),
      distinctUntilChanged(),
      map((text: string) => this.applyFilter(text))
    ).subscribe((filteredData: any) => {
      this.filteredData = filteredData;
    });

    // }

  }

  // ngOnChanges(changes: SimpleChanges): void {
  //   throw new Error('Method not implemented.');
  // }

  async ngAfterViewInit(): Promise<void> {

    // this.landLayers();

    // let geo = L.geoJSON(this.polygon).addTo(this.map);

    let polyg: any = [];

    this.polygon.features.forEach(f => {

      if (f.properties.popupContent !== "") {
        f.geometry.coordinates.forEach(c => {
          c.forEach(coord => {
            coord.reverse();
          });

          polyg.push(c);
          // poligon = L.polygon(c);
        });

        let pol = L.polygon(polyg[0]).addTo(this.map);

        this.allPolygons.push({
          "pol": pol,
          "polName": f.properties.popupContent
        });
        polyg = [];
      } else {
        f.geometry.coordinates.forEach(c => {
          c.forEach(coord => {
            coord.reverse();
          });
        });
      }
    });

  }

  /**
   * FUNZIONE CHE RIMUOVE TUTTI I POLIGONI DALLA MAPPA
   */
  removeAllPolygons() {
    // console.log("allPolygons", this.allPolygons);

    this.allPolygons.forEach(p => {
      this.map.removeLayer(p.pol);
    })
    this.allPolygons = [];
  }

  /**
   * FUNZIONE CHE RIMUOVE I POLIGONI DALLA MAPPA E AGGIUNGE L'AREA ADRIATICA
   */
  adriaticView() {
    let polyg: any = [];
    this.removeAllPolygons();
    this.polygon.features.forEach(f => {
      if (f.properties.popupContent === "") {
        f.geometry.coordinates.forEach(c => {
          polyg.push(c);
          // poligon = L.polygon(c);
        });
        const pol = L.polygon(polyg[0]).addTo(this.map);
        this.allPolygons.push({
          "pol": pol,
          "polName": f.properties.popupContent
        });
        polyg = [];
      }
    });

  }

  /**
   * FUNZIONE CHE MOSTRA I POLIGONI PRECEDENTEMENTE CONFIGURATI SULLA MAPPA
   */
  pilotView() {
    let polyg: any = [];
    this.removeAllPolygons();
    this.polygon.features.forEach(f => {
      f.geometry.coordinates.forEach(c => {
        polyg.push(c);
        // poligon = L.polygon(c);
      });
      const pol = L.polygon(polyg[0]);
      if (f.properties.popupContent !== "") {
        pol.addTo(this.map);
        this.allPolygons.push({
          "pol": pol,
          "polName": f.properties.popupContent
        });
      } else {
        this.map.removeLayer(pol);
      }
      polyg = [];
    });
  }

  /**
   * METODO CHE MOSTRA I DATI DEL POLIGONO CARICATO E SELEZIONATO!
   */
  uploadGeo(): Promise<File> {

    return new Promise((resolve, reject) => {
      const input = document.createElement('input');
      input.type = 'file';
      input.accept = '.geojson';
      input.addEventListener('change', () => {
        const file = input.files?.[0];
        if (file) {
          resolve(file);
          //now we have the file and we read it!
          const reader = new FileReader();

          reader.onload = (e: any) => {
            const content = e.target.result;
            const geojson = JSON.parse(content);
            let polyg: any = [];
            this.removeAllPolygons(); //first we remove all polygons
            geojson.features.forEach((f: any) => {

              f.geometry.coordinates.forEach((c: any) => {
                c.forEach((coord: any) => {
                  coord.reverse();
                });

                polyg.push(c);
                // poligon = L.polygon(c);
              });

              const pol = L.polygon(polyg[0]).addTo(this.map);
              this.allPolygons.push({
                "pol": pol,
                "polName": f.properties.popupContent
              });
              polyg = [];
            });
          }

          reader.readAsText(file);

        } else {
          reject(new Error('No file chosen'));
        }
      });
      input.click();
    });
  }

  async ngOnInit(): Promise<void> {

    await this.initMap();

  }

  async initMap(): Promise<void> {
    this.map = L.map("map");
    this.map.setView(this.center, this.zoom)

    // imposto il layer della mappa prendendolo da openstreetmap assegnando i valori di zoom massimi e minimi
    const tiles = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 18,
      minZoom: 1,
      attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    });

    tiles.addTo(this.map);

  }

  // addPolygons() {

  /**
   * METODO CHE APRE LA MODALE DOVE INSERIRE LE COORDINATE
   */
  openModalSelectCoords() {
    if (this.circleMarkerArray.length > 0) {
      this.circleMarkerArray.forEach((circle: any) => {
        circle.removeEventListener('click');
      });
    }

    this.selectCoords = true;
    const dialogConfig = new MatDialogConfig();

    dialogConfig.disableClose = true;
    dialogConfig.autoFocus = true;
    //dobbiamo passargli la lista dei layers attivi!
    // console.log("this.activeLayersArray =", this.activeLayersArray);

    dialogConfig.data = {
      selectCoords: this.selectCoords,
    };

    const dialogRef = this.dialog.open(SelectCoordsDialogComponent, dialogConfig);
    //prendere i due layers selezionati!
    dialogRef.afterClosed().subscribe(async result => {
      if (result != "") {
        this.pointSelect(result.lat, result.lng);

      }
    })
  }

  /**
   * FUNZIONE CHE PERMETTE DI APRIRE LA MODALE CON IL GRAFICO CORRISPONDENTE AL PUNTO CLICCATO ALL'INTERNO DEL DATASET SULLA MAPPA
   */
  pointSelect(lat?: any, lng?: any) {

    // if(this.pointBoolean === false) {
    // this.pointBoolean = true;
    // }else{
    //   this.pointBoolean = false;
    // }
    // this.pointBoolean = true;
    // '../../assets/geojson/geojson.json'
    // console.log("MAP CONTAINER =", this.map.getContainer().style)

    this.map.off('click');
    this.map.getContainer().style.cursor = "url('../../assets/img/pointer-map-marker-removebg.png') 16 31, auto";
    if (this.datasetCompare === null) {
      this.clickPointOnOff = !this.clickPointOnOff;

    }
    else {
      this.clickPointOnOff = true;
    }
    if (this.circleMarkerArray.length > 0 && !this.clickPointOnOff) {
      this.circleMarkerArray.forEach((circle: any) => {
        circle.removeEventListener('click');
      });
    }
    this.clickPolygonOnOff = false;
    if (this.circleMarkerArray.length > 0 && this.clickPointOnOff) {
      this.circleMarkerArray.forEach((circle: any) => {
        circle.addEventListener('click', (e: any) => this.openGraphDialog(circle.getLatLng().lat, circle.getLatLng().lng));
      });
      this.map.off("click");
      // this.clickPointOnOff = false;
    }
    else {
      // console.log("ENTRO NELL'ELSE QUESTO è IL VALORE DI THIS.SELECTCOORDS",this.selectCoords);
      if (this.selectCoords) {
        // console.log("SONO DENTRO SELECTCOORDS");

        this.map.getContainer().style.cursor = "default";

        this.coordOnClick = {
          lat: lat,
          lng: lng
        }
        let latlng: L.LatLngExpression = [lat, lng];
        this.openGraphDialog();
        const marker = L.marker(latlng, {
          icon: L.icon({
            // iconSize: [25, 41],
            iconSize: [32, 32],
            iconAnchor: [16, 32],
            // iconUrl: 'marker-icon.png',
            iconUrl: '../../assets/img/pointer-map-marker-removebg.png',
          })
        });
        marker.on('click', this.onMarkerClick.bind(this));

        // marker.addTo(this.map);
        this.markers.push(marker);
        if (this.selData.get("dataSetSel")?.value) {
          if (this.markerPoint) {
            this.map.removeLayer(this.markerPoint);
          }
          this.markerPoint = L.marker(latlng, {
            icon: L.icon({
              // iconSize: [25, 41],
              iconSize: [32, 32],
              iconAnchor: [16, 32],
              // iconUrl: 'marker-icon.png',
              iconUrl: '../../assets/img/pointer-map-marker-removebg.png',
            })
          })
            // .bindPopup("Info marker")
            .addTo(this.map)

          const button = document.createElement('button');
          // button.classList.add('btn');
          button.className = 'border btn btn-xs btn-icon px-0 col-3 d-flex flex-row justify-content-center align-items-center';
          button.style.backgroundColor = '#F0F0F0';
          button.innerHTML = "<span class='material-icons col-12' style='color: red; font-size: 20px'>delete</span>";
          // button.innerHTML = "<span class='material-icons col-12' style='color: red;>delete</span>";
          // <button style="background-color: #F0F0F0;" class="border btn btn-xs btn-icon ms-1 col-6 d-flex flex-row justify-content-center align-items-center"
          //         (click)="deleteLayer(); deleteElActiveLayers()" matTooltip="Remove the layer">
          //         <mat-icon [ngStyle]="{'color': 'red'}" class="col-12">delete</mat-icon>
          //         </button>
          // <i class="material-icons" style="font-size:48px;color:red">delete</i>
          button.addEventListener('click', () => {
            this.map.removeLayer(this.markerPoint);
          });

          const lat_lng = this.markerPoint.getLatLng();

          const content = document.createElement('div');
          // content.className = 'd-flex flex-row justify-content-center align-items-center';
          content.style.display = 'flex';
          content.style.flexDirection = 'column';
          content.style.alignItems = 'center';
          content.style.justifyContent = 'center';
          content.innerHTML = "Lat: " + lat_lng.lat.toFixed(5) + ", Lng: " + lat_lng.lng.toFixed(5) + "<br>";
          // content.textContent = "Lat: " + lat_lng.lat.toFixed(5) + ", Lng: " + lat_lng.lng.toFixed(5);
          content.appendChild(button);

          // this.markerPoint.on('click', this.markerPointClick.bind(this));
          if (this.datasetCompare === null) {
            this.markerPoint.on('dblclick', this.markerPointClick.bind(this));

          }

          this.markerPoint.bindPopup(content, {
            offset: [0, -25],
          }).openPopup();

        }

        this.selectCoords = false;

      }
      else {
        if (this.clickPointOnOff === true) {
          this.map.off('click');

          this.map.on('click', this.onMapClick.bind(this));

        }
        else {
          this.map.off('click');
          this.map.getContainer().style.cursor = "default";
          // this.map.on('click', this.onMapClick.bind(this));

        }

      }
    }
    // if(this.markerToAdd) {
    //   this.markerToAdd.addEventListener('click', (e: any) => this.openGraphDialog(this.markerToAdd.getLatLng().lat,this.markerToAdd.getLatLng().lng));

    // }

    // }

    // this.initMap();
  }

  /**
   * FUNZIONE CHE PERMETTE DI APRIRE LA MODALE CON IL GRAFICO CORRISPONDENTE AL POLIGONO CLICCATO ALL'INTERNO DEL DATASET SULLA MAPPA
   */
  polygonSelect() {
    if (this.circleMarkerArray.length > 0) {
      this.circleMarkerArray.forEach((circle: any) => {
        circle.removeEventListener('click');
      });
    }

    if (this.markerPoint) {
      this.map.removeLayer(this.markerPoint);
    }
    this.map.off('click');
    this.map.getContainer().style.cursor = "default";
    this.clickPolygonOnOff = !this.clickPolygonOnOff;
    this.clickPointOnOff = false;
    if (this.clickPolygonOnOff === true) {
      this.map.off('click');
      this.map.on('click', this.onPolygonClick.bind(this));

    }
    else {
      this.map.off('click');
      this.map.getContainer().style.cursor = "default";
      // this.map.on('click', this.onMapClick.bind(this));

    }

  }

  isPointInsidePolygon(coords: any, poly: any) {

    const polyPoints = poly.getLatLngs()[0];

    const x = coords.lat
    const y = coords.lng;

    let inside = false;
    for (let i = 0, j = polyPoints.length - 1; i < polyPoints.length; j = i++) {
      const xi = polyPoints[i].lat, yi = polyPoints[i].lng;
      const xj = polyPoints[j].lat, yj = polyPoints[j].lng;

      const intersect = ((yi > y) != (yj > y))
        && (x < (xj - xi) * (y - yi) / (yj - yi) + xi);
      if (intersect) inside = !inside;
    }

    return inside;
  }

  onPolygonClick = (e: L.LeafletMouseEvent) => {
    // this.map.off('click');
    if (this.activeLayersArray.length === 0) {
      //hai cliccato il bottone e un punto ma non ci sono layer attivi
      this.openGraphDialog();

    } else {
      //console.log("EVENT POLYGON =", e);
      //chiamare il backend prendendo tutti i punti e poi filtrare quelli che sono dentro il poligono
      //è il modo più giusto?
      //oppure prendere tutti i punti e poi filtrare quelli che sono dentro il poligono
      const polygonsContainingPoint = this.allPolygons.filter((polygon: any) => {
        const copiaPoly = _.cloneDeep(polygon);
        // console.log("Polygon copy: ", copiaPoly);
        if (this.isPointInsidePolygon(e.latlng, polygon.pol)) {
          return polygon;
        }
        // if (polygon.pol.getBounds().contains(e.latlng)) {
        //   return polygon;
        // }

        // return polygon.pol.getBounds().contains(e.latlng);
      }); //poligono che contiene il punto in cui l'utente ha cliccato
      // let latLngObj: any[] = [];
      // const bounds = L.latLngBounds(polygonsContainingPoint[0].getLatLngs());
      // // console.log("BOUNDS SOUTH =", bounds.getSouth());
      // // console.log("BOUNDS NORTH =", bounds.getNorth());
      // // console.log("BOUNDS WEST =", bounds.getWest());
      // // console.log("BOUNDS EAST =", bounds.getEast());
      // // console.log("POLYGON CONTAINING POINT =", polygonsContainingPoint);

      // let latlngs: any[] = [];
      if (polygonsContainingPoint.length > 0) {
        //  console.log("POLYGON CONTAINING POINT =", polygonsContainingPoint[0].getLatLngs());
        this.openGraphDialog(null, null, polygonsContainingPoint)
        //   let splittedVar = this.selData.get("dataSetSel")?.value.name.variable_names.split(" ");
        //   splittedVar = splittedVar[splittedVar.length - 1];
        //   this.httpClient.post('http://localhost:8000/test/dataPolygon', {
        //   dataset: this.selData.get("dataSetSel")?.value.name,
        //   selVar: this.selData.get("dataSetSel")?.value.name.griddap_url !== "" ? this.variableGroup.get("variableControl")?.value : splittedVar,
        //   isIndicator: this.isIndicator ? "true" : "false",
        //   selDate: this.formatDate(this.selectedDate.get("dateSel")?.value),
        //   range: this.value ? Math.abs(this.value) : 0,
        //   latLngObj: polygonsContainingPoint[0].getLatLngs()[0]
        // }).subscribe({
        //   next: (res: any) => {
        //     console.log("RES =", res);
        //     let allDataPolygon = res['dataVect'];
        //     let valuesPol = allDataPolygon[0]; //media dei valori
        //     let datesPol = allDataPolygon[1]; //tutte le date!


        //   },
        //   error: (msg: any) => {
        //     console.log('METADATA ERROR: ', msg);
        //   }

        // });

      }
      else {
        alert("Select a polygon");
      }
      // this.allPolygons.forEach((pol: any) => {
      //   if (pol.getBounds().contains(e.latlng)) {
      //     console.log("The polygon is rullo di tamburi", pol);
      //   }
      // });
      // alert("You must select a polygon!"); nel caso in cui non viene selezionato un poligono
    }
  }

  /**
   * METODO RICHIAMATO AL CLICK SULLA MAPPA
   */
  onMapClick = (e: L.LeafletMouseEvent) => {

    if (this.datasetCompare != null) {
      this.clickPointOnOff = false;
      this.map.off('click');
      this.map.getContainer().style.cursor = "default";
    }

    this.coordOnClick = {
      lat: e.latlng.lat,
      lng: e.latlng.lng
    }
    this.openGraphDialog();
    const marker = L.marker(e.latlng, {
      icon: L.icon({
        // iconSize: [25, 41],
        iconSize: [32, 32],
        iconAnchor: [16, 32],
        // iconUrl: 'marker-icon.png',
        iconUrl: '../../assets/img/pointer-map-marker-removebg.png',
      })
    });
    marker.on('click', this.onMarkerClick.bind(this));

    // marker.addTo(this.map);
    this.markers.push(marker);
    if (this.selData.get("dataSetSel")?.value) {
      if (this.markerPoint) {
        this.map.removeLayer(this.markerPoint);
      }
      this.markerPoint = L.marker(e.latlng, {
        icon: L.icon({
          // iconSize: [25, 41],
          iconSize: [32, 32],
          iconAnchor: [16, 32],
          // iconUrl: 'marker-icon.png',
          iconUrl: '../../assets/img/pointer-map-marker-removebg.png',
        })
      })
        // .bindPopup("Info marker")
        .addTo(this.map)

      const button = document.createElement('button');
      // button.classList.add('btn');
      button.className = 'border btn btn-xs btn-icon px-0 col-3 d-flex flex-row justify-content-center align-items-center';
      button.style.backgroundColor = '#F0F0F0';
      button.innerHTML = "<span class='material-icons col-12' style='color: red; font-size: 20px'>delete</span>";
      // button.innerHTML = "<span class='material-icons col-12' style='color: red;>delete</span>";
      // <button style="background-color: #F0F0F0;" class="border btn btn-xs btn-icon ms-1 col-6 d-flex flex-row justify-content-center align-items-center"
      //         (click)="deleteLayer(); deleteElActiveLayers()" matTooltip="Remove the layer">
      //         <mat-icon [ngStyle]="{'color': 'red'}" class="col-12">delete</mat-icon>
      //         </button>
      // <i class="material-icons" style="font-size:48px;color:red">delete</i>
      button.addEventListener('click', () => {
        this.map.removeLayer(this.markerPoint);
      });

      const lat_lng = this.markerPoint.getLatLng();

      const content = document.createElement('div');
      // content.className = 'd-flex flex-row justify-content-center align-items-center';
      content.style.display = 'flex';
      content.style.flexDirection = 'column';
      content.style.alignItems = 'center';
      content.style.justifyContent = 'center';
      content.innerHTML = "Lat: " + lat_lng.lat.toFixed(5) + ", Lng: " + lat_lng.lng.toFixed(5) + "<br>";
      // content.textContent = "Lat: " + lat_lng.lat.toFixed(5) + ", Lng: " + lat_lng.lng.toFixed(5);
      content.appendChild(button);

      // this.markerPoint.on('click', this.markerPointClick.bind(this));
      if (this.datasetCompare === null) {
        this.markerPoint.on('dblclick', this.markerPointClick.bind(this));

      }

      this.markerPoint.bindPopup(content, {
        offset: [0, -25],
      }).openPopup();

    }
  }

  markerPointClick() {
    // console.log("MARKER POINT CLICKED");
    this.openGraphDialog();

  }

  removeMarker() {
    // this.map.removeLayer(this.markerPoint);
    // console.log("SONO DENTRO REMOVE MARKER");
  }

  onMarkerClick(event: any) {
    // console.log("MARKER CLICKED");
    const marker = event.target;

    this.map.removeLayer(marker);
    this.markers = this.markers.filter(m => m !== marker);
  }

  openMyMenu(menuTrigger: MatMenuTrigger) {

    // menuTrigger.openMenu();
    menuTrigger.openMenu();
  }

  closeMyMenu(menuTrigger: MatMenuTrigger) {
    menuTrigger.closeMenu();
  }

  getPluto() {
    this.httpService.post('test/pluto', {
    }).subscribe({
      next(position: any) {
        // console.log("PLUTO =", position);

      },
      error(msg: any) {
        // console.log('PLUTO ERROR: ', msg);
      }
    });
  }

  /**
   * FUNZIONE CHE RICHIAMA TUTTI I NUOVI DATASET DI ERDDAP ATTRAVERSO I SERVIZI API COLLEGATI AI NODI DEL DATABASE
   */
  getAllNodes() {
    this.categoryDatasets = [];
    this.indicators = [];
    this.models = [];
    this.observations = [];
    this.reanallysis = [];

    let tmpCategoryDatasets: any[] = [];
    let tmpScale: any[] = [];
    let tmpTimeperiods: any[] = [];

    this.httpService.post('test/allNodes', {
    }).subscribe({
      next: (res: any) => {
        // console.log("SUB NEXT");
        console.log("RES NODES =", res.nodes);

        this.resAllNodes = res.nodes;

        this.resAllNodes.forEach((element: any) => {
          if(element.adriaclim_dataset !== "no" && element.adriaclim_dataset !== "No" && element.adriaclim_dataset !== "Indicator") {
            tmpCategoryDatasets.push(element.adriaclim_dataset);
          }
        });
        this.categoryDatasets = [...new Set(tmpCategoryDatasets)];
        this.formMenuDatasets.get("category")?.setValue(this.categoryDatasets[0]);

        this.resAllNodes.forEach((el: any) => {
          if(el.adriaclim_dataset === this.formMenuDatasets.get("category")?.value) {
            tmpScale.push(el.adriaclim_scale);
          }
        });
        this.scaleDatasets = [...new Set(tmpScale)];
        this.formMenuDatasets.get("scale")?.setValue(this.scaleDatasets[0]);

        this.resAllNodes.forEach((el: any) => {
          if (el.adriaclim_dataset === this.formMenuDatasets.get("category")?.value && el.adriaclim_scale === this.formMenuDatasets.get("scale")?.value) {
            tmpTimeperiods.push(el.adriaclim_timeperiod);
          }
        });
        this.timeperiodDatasets = [...new Set(tmpTimeperiods)];
        this.formMenuDatasets.get("timeperiod")?.setValue(this.timeperiodDatasets[0]);

        this.menuDatasets = this.resAllNodes.filter((el: any) => el.adriaclim_dataset === this.formMenuDatasets.get("category")?.value && el.adriaclim_scale === this.formMenuDatasets.get("scale")?.value && el.adriaclim_timeperiod === this.formMenuDatasets.get("timeperiod")?.value);

        console.log("CATEGORY DATASETS =", this.categoryDatasets);
        console.log("SCALE DATASETS =", this.scaleDatasets);
        console.log("TIMEPERIOD DATASETS =", this.timeperiodDatasets);
        console.log("MENU DATASETS =", this.menuDatasets);
        console.log("FORM MENU DATASETS =", this.formMenuDatasets.value);


        // console.log("PRIMO ELEMENTO DI CATEGORY DATASETS =", this.categoryDatasets[0]);
        // console.log("indicators =", this.indicators);
        // console.log("models =", this.models);
        // console.log("observations =", this.observations);
        // console.log("reanallysis =", this.reanallysis);

        // res.nodes.forEach((node: any) => {

        //   //riempiamo tree con tutti i nodi
        //   if (node.adriaclim_dataset === "indicator") {
        //     const indicatori = TREE_DATA.filter((indicators: any) => indicators.name === "Indicators")[0];
        //     //creare figli automaticamente in base al valore di adriaclim_scale e adriaclim_timeperiod
        //     const scaleUpperCase = node.adriaclim_scale.charAt(0).toUpperCase() + node.adriaclim_scale.slice(1);
        //     if (indicatori?.children?.findIndex(scaleIndicator => scaleIndicator.name.toLowerCase() === node.adriaclim_scale.toLowerCase()) === -1) {
        //       indicatori?.children?.push({
        //         name: scaleUpperCase,
        //         children: []
        //       });
        //     }

        //     // ordina in senso alfabetico la parte relativa agli scale del modello
        //     indicatori?.children?.sort((o1: any, o2: any) => {
        //       if (o1.name > o2.name) {
        //         return 1;
        //       }
        //       if (o1.name < o2.name) {
        //         return -1;
        //       }
        //       return 0;
        //     })

        //     const scale = indicatori.children?.filter((sca: any) => sca.name.toLowerCase().includes(node.adriaclim_scale.toLowerCase()))[0];
        //     const timeUpperCase = node.adriaclim_timeperiod.charAt(0).toUpperCase() + node.adriaclim_timeperiod.slice(1);
        //     if (scale?.children?.findIndex(timeInd => timeInd.name.toLowerCase() === node.adriaclim_timeperiod.toLowerCase()) === -1) {
        //       scale?.children?.push({
        //         name: timeUpperCase,
        //         children: []
        //       });
        //     }

        //     //ordina in senso alfabetico la parte relativa ai timeperiod del modello
        //     scale?.children?.sort((o1: any, o2: any) => {
        //       if (o1.name > o2.name) {
        //         return 1;
        //       }
        //       if (o1.name < o2.name) {
        //         return -1;
        //       }
        //       return 0;
        //     })

        //     const time = scale?.children?.filter((time: any) => time.name.toLowerCase().includes(node.adriaclim_timeperiod.toLowerCase()))[0];
        //     if (time?.children?.findIndex(elModel => elModel.name === node.title) === -1) {
        //       time?.children?.push({
        //         name: node
        //       });
        //       indicatori?.children?.sort((o1: any, o2: any) => {
        //         if (o1.name.title > o2.name.title) {
        //           return 1;
        //         }
        //         if (o1.name.title < o2.name.title) {
        //           return -1;
        //         }
        //         return 0;
        //       })
        //     }
        //   }
        //   else if (node.adriaclim_dataset === "model") {
        //     const modelli = TREE_DATA.filter((models: any) => models.name === "Numerical models")[0]
        //     //creare figli automaticamente in base al valore di adriaclim_scale e adriaclim_timeperiod
        //     const scaleUpperCase = node.adriaclim_scale.charAt(0).toUpperCase() + node.adriaclim_scale.slice(1);
        //     if (modelli?.children?.findIndex(scaleModel => scaleModel.name.toLowerCase() === node.adriaclim_scale.toLowerCase()) === -1) {
        //       modelli?.children?.push({
        //         name: scaleUpperCase,
        //         children: []
        //       });
        //     }

        //     //ordina in senso alfabetico la parte relativa agli scale del modello
        //     modelli?.children?.sort((o1: any, o2: any) => {
        //       if (o1.name > o2.name) {
        //         return 1;
        //       }
        //       if (o1.name < o2.name) {
        //         return -1;
        //       }
        //       return 0;
        //     })

        //     const scale = modelli.children?.filter((sca: any) => sca.name.toLowerCase().includes(node.adriaclim_scale.toLowerCase()))[0];
        //     const timeUpperCase = node.adriaclim_timeperiod.charAt(0).toUpperCase() + node.adriaclim_timeperiod.slice(1);
        //     if (scale?.children?.findIndex(timeModel => timeModel.name.toLowerCase() === node.adriaclim_timeperiod.toLowerCase()) === -1) {
        //       scale?.children?.push({
        //         name: timeUpperCase,
        //         children: []
        //       });
        //     }

        //     //ordina in senso alfabetico la parte relativa ai timeperiod del modello
        //     scale?.children?.sort((o1: any, o2: any) => {
        //       if (o1.name > o2.name) {
        //         return 1;
        //       }
        //       if (o1.name < o2.name) {
        //         return -1;
        //       }
        //       return 0;
        //     })

        //     const time = scale?.children?.filter((time: any) => time.name.toLowerCase().includes(node.adriaclim_timeperiod.toLowerCase()))[0];
        //     if (time?.children?.findIndex(elModel => elModel.name === node.title) === -1) {
        //       time?.children?.push({
        //         name: node
        //       });
        //       modelli?.children?.sort((o1: any, o2: any) => {
        //         if (o1.name.title > o2.name.title) {
        //           return 1;
        //         }
        //         if (o1.name.title < o2.name.title) {
        //           return -1;
        //         }
        //         return 0;
        //       })
        //     }
        //   }
        //   else if (node.adriaclim_dataset === "observation") {
        //     const observation = TREE_DATA.filter((obs: any) => obs.name === "Observations")[0];
        //     //creare figli automaticamente in base al valore di adriaclim_scale e adriaclim_timeperiod
        //     const scaleUpperCase = node.adriaclim_scale.charAt(0).toUpperCase() + node.adriaclim_scale.slice(1);
        //     if (observation?.children?.findIndex(scaleModel => scaleModel.name.toLowerCase() === node.adriaclim_scale.toLowerCase()) === -1) {
        //       observation?.children?.push({
        //         name: scaleUpperCase,
        //         children: []
        //       });
        //     }

        //     //ordina in senso alfabetico la parte relativa agli scale di observations
        //     observation?.children?.sort((o1: any, o2: any) => {
        //       if (o1.name > o2.name) {
        //         return 1;
        //       }
        //       if (o1.name < o2.name) {
        //         return -1;
        //       }
        //       return 0;
        //     })

        //     const scale = observation.children?.filter((sca: any) => sca.name.toLowerCase().includes(node.adriaclim_scale.toLowerCase()))[0];
        //     const timeUpperCase = node.adriaclim_timeperiod.charAt(0).toUpperCase() + node.adriaclim_timeperiod.slice(1);
        //     if (scale?.children?.findIndex(timeModel => timeModel.name.toLowerCase() === node.adriaclim_timeperiod.toLowerCase()) === -1) {
        //       scale?.children?.push({
        //         name: timeUpperCase,
        //         children: []
        //       });
        //     }

        //     //ordina in senso alfabetico la parte relativa ai timeperiod di observations
        //     scale?.children?.sort((o1: any, o2: any) => {
        //       if (o1.name > o2.name) {
        //         return 1;
        //       }
        //       if (o1.name < o2.name) {
        //         return -1;
        //       }
        //       return 0;
        //     })

        //     const time = scale?.children?.filter((time: any) => time.name.toLowerCase().includes(node.adriaclim_timeperiod.toLowerCase()))[0];
        //     if (time?.children?.findIndex(elModel => elModel.name === node.title) === -1) {
        //       time?.children?.push({
        //         name: node
        //       });

        //       observation?.children?.sort((o1: any, o2: any) => {
        //         if (o1.name.title > o2.name.title) {
        //           return 1;
        //         }
        //         if (o1.name.title < o2.name.title) {
        //           return -1;
        //         }
        //         return 0;
        //       })

        //     }

        //   }
        //   this.dataAllNodes.push(
        //     { name: node }
        //   );

        // });

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

        // console.log("DATA ALL NODES =", this.dataAllNodes);
        // console.log("DATA ALL NODES TREE =", this.dataAllNodesTree.data);


      },
      error: (msg: any) => {
        console.log("SUB ERROR");

        console.log('ALL NODES ERROR: ', msg);
      }
    })
    // this.dataSource.data = TREE_DATA;

  }

  /**
   * FUNZIONE CHE RITORNA TUTTI I DATI PER POPOLARE POI IL TREE
   */
  getInd() {
    this.httpService.post('test/ind', {
    }).subscribe({
      next: (res: any) => {

        this.dataInd = res.ind;

        this.dataInd.forEach((ind: any) => {
          const indicatori = TREE_DATA.filter((node: any) => node.name === "Indicators")[0]
          const scale = indicatori.children?.filter((sca: any) => sca.name.toLowerCase().includes(ind.adriaclim_scale.toLowerCase()))[0];
          const time = scale?.children?.filter((time: any) => time.name.toLowerCase().includes(ind.adriaclim_timeperiod.toLowerCase()))[0];
          if (time?.children?.findIndex(title => title.name === ind.title) === -1) {
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

  /**
   * FUNZIONE CHE POPOLA LA LISTA DEI LAYER ATTIVI NEL PANNELLO ACTIVE LAYERS
   */
  addToActiveLayers(node: any) {
    if (this.activeLayersArray.indexOf(node) === -1) {
      this.activeLayersArray.push(node);
    }

    this.selData.get("dataSetSel")?.setValue(node);
    this.isIndicator = this.selData.get("dataSetSel")?.value.name.griddap_url !== "" ? false : true;
    if (!this.isIndicator) {
      this.legendNoWms = undefined;
    }
  }

  /**
   * FUNZIONE CHE VIENE LANCIATA OGNI VOLTA CHE SI CAMBIA LA SELEZIONE DEL LAYER ATTRAVERSO LA LISTA DEGLI ACTIVE LAYERS PER AGGIORNARE LA MAPPA
   */
  selActiveLayer(event: any) {

    let metaId: any;
    if (this.selData.get("dataSetSel")?.value.name.dataset_id) {
      metaId = this.selData.get("dataSetSel")?.value.name.dataset_id;

    }

    else if (this.selData.get("dataSetSel")?.value.name.id) {
      metaId = this.selData.get("dataSetSel")?.value.name.id;
    }

    if (this.selData.get("dataSetSel")?.value.name.wms_url !== "") {
      //se non è vettoriale abilito il click sulla mappa!
      if (this.clickPointOnOff) {
        this.map.off('click');
        this.map.on('click', this.onMapClick.bind(this));
      }
    }

    this.getSelectedNode(event.value);
    this.getMeta(metaId);
  }

  /**
   * FUNZIONE CHE PERMETTE DI RECUPERARE I METADATA SEI DATASET
   */
  getMeta(idMeta: any, controlDate?: any, controlExtra?: any) {


    if (this.legendLayer_src || this.legendNoWms) {
      this.deleteLayer(idMeta);

    }
    this.httpService.post('test/metadata', {
      idMeta: idMeta
    }).subscribe({
      next: (res: any) => {
        if (this.circleMarkerArray.length > 0) {
          this.circleMarkerArray.forEach((circle: any) => {
            circle.removeEventListener('click');
          });
        } else {
          if (this.clickPointOnOff) {
            this.map.off('click');
            this.map.on('click', this.onMapClick.bind(this));
          }
        }
        this.metadata = res;
        // console.log("METADATA =", this.metadata);
        // console.log("Id meta======", idMeta);

        if (controlDate === "ok") {

          this.getLayers(idMeta, controlDate, controlExtra);
        }
        else {
          this.getLayers(idMeta);
        }
      },
      error: (msg: any) => {
        console.log('METADATA ERROR: ', msg);
      }

    });

  }

  /**
   * FUNZIONE CHE PRENDE IN INPUT IL NODO E GESTISCE LE SUE INFORMAZIONI PER ESEMPIO LE VARIABILI
   */
  getSelectedNode(node: any) {
    this.variableArray = [];

    if (node.name) {
      let variableNames = node.name.variable_names.split(" ");
      let variableTypes = node.name.variable_types.split(" ");
      // console.log("VariableName===========", variableNames, "variable types==========", variableTypes);
      variableNames.forEach((variableName: any, index: number) => {
        // Include variables that are not "time", "latitude", or "longitude" and have a type of "float"

        if (
          variableName !== "time" && variableName !== "latitude" && variableName !== "longitude" &&
          (variableTypes[index] !== "float" || variableTypes[index] !== "double")
        ) {

          this.variableArray.push({ name: variableName, type: variableTypes[index] });
        }
      });
      // console.log("Test===========",test);
      // this.variableArray = node.name.variable_names.split(" ");
    }
    else if (node.variable_names) {
      let variableNames = node.variable_names.split(" ");
      let variableTypes = node.variable_types.split(" ")

      variableNames.forEach((variableName: any, index: number) => {
        if (
          variableName !== "time" && variableName !== "latitude" && variableName !== "longitude" &&
          (variableTypes[index] !== "float" || variableTypes[index] !== "double")
        ) {
          this.variableArray.push({ name: variableName, type: variableTypes[index] });
        }
      });
      // console.log("Test===========",test);
      // this.variableArray = node.variable_names.split(" ");
    }
    // this.isIndicator = node.name.griddap_url !== "" ? false : true; //true se è tabledap, false se è griddap
    // if (this.isIndicator) {

    //   this.variableArray = this.variableArray.slice(-1);
    // }
    // console.log("thisVariableArray: ", this.variableArray);

    if(this.variableArray.length > 0) {
      this.variableGroup.get("variableControl")?.setValue(this.variableArray[this.variableArray.length - 1]["name"]);

    }

  }

  /**
   * FUNZIONE CHE PERMETTE DI RECUPERARE L'ULTIMO GIORNO DEL MESE
   */
  lastday(y: any, m: any) {

    return new Date(y, m + 1, 0).getDate();
  }

  /**
   * FUNZIONE CHE RITORNA IL MESE REALE SUCCESSIVO
   */
  addRealMonth(d: any, months: any) {
    const fm = moment(d).add(months, 'M');
    const fmEnd = moment(fm).endOf('month');
    return d.date() != fm.date() && fm.isSame(fmEnd.format('YYYY-MM-DD')) ? fm.add(1, 'd') : fm;
  }

  /**
   * FUNZIONE CHE RITORNA IL MESE REALE PRECEDENTE
   */
  subtractRealMonth(d: any, months: any) {
    const fm = moment(d).subtract(months, 'M');
    const fmEnd = moment(fm).endOf('month');
    return d.date() != fm.date() && fm.isSame(fmEnd.format('YYYY-MM-DD')) ? fm.add(1, 'd') : fm;
  }

  subtractLastDayMonth(d: any, months: any) {
    return moment(d).subtract(months, 'months').endOf('month').toDate();
  }

  addLastDayMonth(d: any, months: any) {
    return moment(d).add(months, 'months').endOf('month').toDate();
  }

  isLastDayOfMonth(d: any) {
    d.setDate(d.getDate() + 1);
    if (d.getDate() === 1) {
      return true;
    } else {
      return false;
    }
  }

  isAString(val: any): boolean { return typeof val === 'string'; }

  /**
   * FUNZIONE CHE PERMETTE DI GESTIRE OGNI CASISTICA LEGATA AI BOTTONI PER IL CAMBIO DATA
   */
  changeDate(arrow: any) {

    let metaId: any;
    if (this.selData.get("dataSetSel")?.value.name.dataset_id) {
      metaId = this.selData.get("dataSetSel")?.value.name.dataset_id;

    }

    else if (this.selData.get("dataSetSel")?.value.name.id) {
      metaId = this.selData.get("dataSetSel")?.value.name.id;
    }

    if (arrow === "leftAll") {
      this.selectedDate.get("dateSel")?.setValue(this.dateStart);
      //leftAll is clicked so we disable left button and enable the right ones
      this.navigateDateLeftYear = true;
      this.navigateDateRightYear = false;
      this.navigateDateRightMonth = false;
      this.navigateDateRightSeason = false;
      this.navigateDateLeftMonth = false;
      this.navigateDateLeftSeason = false;
      this.getMeta(metaId, "ok", this.valueCustom);
    }
    else if (arrow === "rightAll") {
      //rightAll is clicked so we disable right button and enable the left ones
      this.selectedDate.get("dateSel")?.setValue(this.dateEnd);
      this.navigateDateRightYear = true;
      this.navigateDateLeftYear = false;
      this.navigateDateLeftSeason = false;
      this.navigateDateLeftMonth = false;
      this.navigateDateRightMonth = false;
      this.navigateDateRightSeason = false;
      this.getMeta(metaId, "ok", this.valueCustom);
    }
    /**
     * GET LAYER 3D
     */
    /**
     * SLIDER
     */
    if (this.selData.get("dataSetSel")?.value.name.adriaclim_timeperiod === "yearly") {
      if (arrow === "left") {

        const selD = _.cloneDeep(this.selectedDate.get("dateSel")?.value);
        if ((selD.getFullYear() - 1) === this.dateStart.getFullYear()) {
          //it is the first year visible so after setting the new value we disable the left button
          selD.setFullYear(selD.getFullYear() - 1);
          this.selectedDate.get("dateSel")?.setValue(selD);
          this.navigateDateLeftYear = true;
          this.navigateDateRightYear = false;
          this.navigateDateRightMonth = false;
          this.navigateDateRightSeason = false;
          this.getMeta(metaId, "ok", this.valueCustom);
        } else {
          selD.setFullYear(selD.getFullYear() - 1);
          this.selectedDate.get("dateSel")?.setValue(selD);
          this.navigateDateLeftYear = false;
          this.navigateDateRightYear = false;
          this.navigateDateRightMonth = false;
          this.navigateDateRightSeason = false;
          this.getMeta(metaId, "ok", this.valueCustom);
        }
      }
      else if (arrow === "right") {
        const selD = _.cloneDeep(this.selectedDate.get("dateSel")?.value);
        if ((selD.getFullYear() + 1) === this.dateEnd.getFullYear()) {
          selD.setFullYear(selD.getFullYear() + 1);
          this.selectedDate.get("dateSel")?.setValue(selD);
          this.navigateDateRightYear = true;
          this.navigateDateLeftYear = false;
          this.getMeta(metaId, "ok", this.valueCustom);
        } else {
          selD.setFullYear(selD.getFullYear() + 1);
          this.selectedDate.get("dateSel")?.setValue(selD);
          this.navigateDateRightYear = false;
          this.navigateDateLeftYear = false;
          this.getMeta(metaId, "ok", this.valueCustom);
        }

      }
    }
    else if (this.selData.get("dataSetSel")?.value.name.adriaclim_timeperiod === "monthly") {
      if (arrow === "left") {
        let selD = _.cloneDeep(this.selectedDate.get("dateSel")?.value);
        const d1 = _.cloneDeep(selD);
        if (this.isLastDayOfMonth(d1)) {
          //SIAMO ALL'ULTIMO GIORNO DEL MESE, GESTIRE QUESTO CASO
          let d2 = _.cloneDeep(selD);
          d2 = this.subtractLastDayMonth(d2, 1);
          d2.setHours(this.dateStart.getHours(), this.dateStart.getMinutes(), this.dateStart.getSeconds());
          if (d2.toString() === this.dateStart.toString()) {
            //ULTIMO GIORNO DEL MESE E PRIMA DATA!
            selD = d2;
            this.selectedDate.get("dateSel")?.setValue(selD);
            this.navigateDateLeftMonth = true;
            this.navigateDateRightMonth = false;
            this.navigateDateRightSeason = false;
            this.navigateDateRightYear = false;
            this.navigateDateLeftYear = false;
            this.navigateDateLeftSeason = false;
            this.getMeta(metaId, "ok", this.valueCustom);
          } else {
            selD = d2;
            this.selectedDate.get("dateSel")?.setValue(selD);
            this.navigateDateLeftMonth = false;
            this.navigateDateRightMonth = false;
            this.navigateDateRightSeason = false;
            this.navigateDateRightYear = false;
            this.navigateDateLeftYear = false;
            this.navigateDateLeftSeason = false;
            this.getMeta(metaId, "ok", this.valueCustom);
          }


        } else {
          //NON SIAMO ALL'ULTIMO GIORNO DEL MESE!
          let d2 = _.cloneDeep(selD);
          d2 = this.subtractRealMonth(moment(d2), 1).toDate();
          d2.setHours(this.dateStart.getHours(), this.dateStart.getMinutes(), this.dateStart.getSeconds());
          if (d2.toString() === this.dateStart.toString()) {
            //ULTIMA DATA!
            selD = d2;
            this.selectedDate.get("dateSel")?.setValue(selD);
            this.navigateDateLeftMonth = true;
            this.navigateDateRightMonth = false;
            this.navigateDateRightSeason = false;
            this.navigateDateRightYear = false;
            this.navigateDateLeftYear = false;
            this.navigateDateLeftSeason = false;
            this.getMeta(metaId, "ok", this.valueCustom);
          } else {
            selD = d2;
            this.selectedDate.get("dateSel")?.setValue(selD);
            this.navigateDateLeftMonth = false;
            this.navigateDateRightMonth = false;
            this.navigateDateRightSeason = false;
            this.navigateDateRightYear = false;
            this.navigateDateLeftYear = false;
            this.navigateDateLeftSeason = false;
            this.getMeta(metaId, "ok", this.valueCustom);
          }
        }
      }
      else if (arrow === "right") {

        let selD = _.cloneDeep(this.selectedDate.get("dateSel")?.value);
        const d1 = _.cloneDeep(selD);
        if (this.isLastDayOfMonth(d1)) {
          //SIAMO ALL'ULTIMO GIORNO DEL MESE, GESTIRE QUESTO CASO
          let d2 = _.cloneDeep(selD);
          d2 = this.addLastDayMonth(d2, 1);
          d2.setHours(this.dateEnd.getHours(), this.dateEnd.getMinutes(), this.dateEnd.getSeconds());
          if (d2.toString() === this.dateEnd.toString()) {
            //ULTIMO GIORNO DEL MESE E PRIMA DATA!
            selD = d2;
            this.selectedDate.get("dateSel")?.setValue(selD);
            this.navigateDateLeftMonth = false;
            this.navigateDateRightMonth = true;
            this.navigateDateRightSeason = false;
            this.navigateDateRightYear = false;
            this.navigateDateLeftYear = false;
            this.navigateDateLeftSeason = false;
            this.getMeta(metaId, "ok", this.valueCustom);
          } else {
            selD = d2;
            this.selectedDate.get("dateSel")?.setValue(selD);
            this.navigateDateLeftMonth = false;
            this.navigateDateLeftYear = false;
            this.navigateDateLeftSeason = false;
            this.navigateDateRightMonth = false;
            this.navigateDateRightSeason = false;
            this.navigateDateRightYear = false;
            this.getMeta(metaId, "ok", this.valueCustom);
          }


        } else {
          //NON SIAMO ALL'ULTIMO GIORNO DEL MESE!
          let d2 = _.cloneDeep(selD);
          d2 = this.addRealMonth(moment(d2), 1).toDate();
          d2.setHours(this.dateEnd.getHours(), this.dateEnd.getMinutes(), this.dateEnd.getSeconds());
          if (d2.toString() === this.dateEnd.toString()) {
            //ULTIMA DATA!
            selD = d2;
            this.selectedDate.get("dateSel")?.setValue(selD);
            this.navigateDateLeftMonth = false;
            this.navigateDateRightMonth = true;
            this.navigateDateRightSeason = false;
            this.navigateDateRightYear = false;
            this.navigateDateLeftYear = false;
            this.navigateDateLeftSeason = false;
            this.getMeta(metaId, "ok", this.valueCustom);
          } else {
            selD = d2;
            this.selectedDate.get("dateSel")?.setValue(selD);
            this.navigateDateLeftMonth = false;
            this.navigateDateLeftYear = false;
            this.navigateDateLeftSeason = false;
            this.navigateDateRightMonth = false;
            this.navigateDateRightSeason = false;
            this.navigateDateRightYear = false;
            this.getMeta(metaId, "ok", this.valueCustom);
          }
        }
      }
    }
    else if (this.selData.get("dataSetSel")?.value.name.adriaclim_timeperiod === "seasonal") {
      if (arrow === "left") {
        let selD = _.cloneDeep(this.selectedDate.get("dateSel")?.value);
        //if(selD.getMonth() === 0) { //NON VA FATTO QUESTO CHECK!!!!
        // selD.setMonth(9);
        // selD.setFullYear(selD.getFullYear() - 1);
        const d1 = _.cloneDeep(selD);
        if (this.isLastDayOfMonth(d1)) {
          //SIAMO ALL'ULTIMO GIORNO DEL MESE!!!!!!!!!
          let d2 = _.cloneDeep(selD);
          d2 = this.subtractLastDayMonth(d2, 3);
          d2.setHours(this.dateStart.getHours(), this.dateStart.getMinutes(), this.dateStart.getSeconds());
          if (d2 <= this.dateStart) {
            selD = d2;
            this.selectedDate.get("dateSel")?.setValue(selD);
            this.navigateDateLeftMonth = false;
            this.navigateDateLeftYear = false;
            this.navigateDateLeftSeason = true;
            this.navigateDateRightMonth = false;
            this.navigateDateRightSeason = false;
            this.navigateDateRightYear = false;
            this.getMeta(metaId, "ok", this.valueCustom);

          } else {
            selD = d2;
            this.selectedDate.get("dateSel")?.setValue(selD);
            this.navigateDateLeftMonth = false;
            this.navigateDateLeftYear = false;
            this.navigateDateLeftSeason = false;
            this.navigateDateRightMonth = false;
            this.navigateDateRightSeason = false;
            this.navigateDateRightYear = false;
            this.getMeta(metaId, "ok", this.valueCustom);
          }

        } else {
          //NON SIAMO ALL'ULTIMO GIORNO DEL MESE
          let d2 = _.cloneDeep(selD);
          d2 = this.subtractRealMonth(moment(d2), 3).toDate();
          d2.setHours(this.dateStart.getHours(), this.dateStart.getMinutes(), this.dateStart.getSeconds());
          if (d2 <= this.dateStart) {
            //ULTIMA DATA!
            selD = d2;
            this.selectedDate.get("dateSel")?.setValue(selD);
            this.navigateDateLeftMonth = false;
            this.navigateDateRightMonth = false;
            this.navigateDateRightSeason = false;
            this.navigateDateRightYear = false;
            this.navigateDateLeftYear = false;
            this.navigateDateLeftSeason = true;
            this.getMeta(metaId, "ok", this.valueCustom);
          } else {
            selD = d2;
            this.selectedDate.get("dateSel")?.setValue(selD);
            this.navigateDateLeftMonth = false;
            this.navigateDateRightMonth = false;
            this.navigateDateRightSeason = false;
            this.navigateDateRightYear = false;
            this.navigateDateLeftYear = false;
            this.navigateDateLeftSeason = false;
            this.getMeta(metaId, "ok", this.valueCustom);
          }
        }

      } //FINE ARROW LEFT!!
      else if (arrow === "right") {
        let selD = _.cloneDeep(this.selectedDate.get("dateSel")?.value);
        const d1 = _.cloneDeep(selD);
        // if(selD.getMonth() === 9) { NON VA FATTO QUESTO CHECK!

        // selD.setMonth(0);
        // selD.setFullYear(selD.getFullYear() + 1);
        if (this.isLastDayOfMonth(d1)) {
          //SIAMO A RIGHT E ALL'ULTIMO GIORNO DEL MESE CASE!
          let d2 = _.cloneDeep(selD);
          d2 = this.addLastDayMonth(d2, 3);
          d2.setHours(this.dateEnd.getHours(), this.dateEnd.getMinutes(), this.dateEnd.getSeconds());
          if (d2 >= this.dateEnd) {
            //ULTIMA DATA!
            selD = d2;
            this.selectedDate.get("dateSel")?.setValue(selD);
            this.navigateDateLeftMonth = false;
            this.navigateDateRightMonth = false;
            this.navigateDateRightSeason = true;
            this.navigateDateRightYear = false;
            this.navigateDateLeftYear = false;
            this.navigateDateLeftSeason = false;
            this.getMeta(metaId, "ok", this.valueCustom);
          } else {
            selD = d2;
            this.selectedDate.get("dateSel")?.setValue(selD);
            this.navigateDateLeftMonth = false;
            this.navigateDateRightMonth = false;
            this.navigateDateRightSeason = false;
            this.navigateDateRightYear = false;
            this.navigateDateLeftYear = false;
            this.navigateDateLeftSeason = false;
            this.getMeta(metaId, "ok", this.valueCustom);
          }
        } else {
          //NON SIAMO ALL'ULTIMO GIORNO DEL MESE!!!!!!!
          let d2 = _.cloneDeep(selD);
          d2 = this.addRealMonth(moment(d2), 3).toDate();
          d2.setHours(this.dateEnd.getHours(), this.dateEnd.getMinutes(), this.dateEnd.getSeconds());
          if (d2 >= this.dateEnd) {
            //ULTIMA DATA POSSIBILE
            selD = d2;
            this.selectedDate.get("dateSel")?.setValue(selD);
            this.navigateDateLeftMonth = false;
            this.navigateDateRightMonth = false;
            this.navigateDateRightSeason = true;
            this.navigateDateRightYear = false;
            this.navigateDateLeftYear = false;
            this.navigateDateLeftSeason = false;
            this.getMeta(metaId, "ok", this.valueCustom);
          } else {
            selD = d2;
            this.selectedDate.get("dateSel")?.setValue(selD);
            this.navigateDateLeftMonth = false;
            this.navigateDateRightMonth = false;
            this.navigateDateRightSeason = false;
            this.navigateDateRightYear = false;
            this.navigateDateLeftYear = false;
            this.navigateDateLeftSeason = false;
            this.getMeta(metaId, "ok", this.valueCustom);
          }
        }

        //}
      } //FINE ELSE IF RIGHT
    } // FINE SEASONAL
    if (this.dateStart?.toString() === this.dateEnd?.toString()) {
      this.navigateDateLeftYear = true;
      this.navigateDateRightYear = true;
      this.navigateDateLeftMonth = true;
      this.navigateDateRightMonth = true;
      this.navigateDateLeftSeason = true;
      this.navigateDateRightSeason = true;
    }
  } //FINE CHANGE DATE

  dateFilter = (date: Date | null): boolean => { return true; }

  /**
   * FUNZIONE CHE GESTISCE IL PARAMETRO AGGIUNTIVO PER IL CASO SENZA WMS MOSTRANDO, DOVE C'E' IL PARAMETRO, IL NOME E I VALORI CORRETTI
   */
  extraParamNoWms(metadata: any, controlExtra?: any) {
    const num_parameters = metadata[0][1].split(", ");
    const min_max_value = metadata[0][0].split(",");
    const name = num_parameters[1];
    const min = Number(min_max_value[0]);
    const max = Number(min_max_value[1]);
    const step = Number(metadata[0][5].split("=")[1]);

    // console.log("ENTRO NEL CASO DEL PARAMETRO AGGIUNTIVO!");
    // console.log("NOME PARAMETRO AGGIUNTIVO======",name);
    // console.log("VALORE MIN",min);
    // console.log("VALORE MAX",max);
    // console.log("STEP",step);

    //se non c'è ci sono questi due if, se c'è hai sempre
    if (name === "depth") {
      // this.extraParam.name = "elevation";
      this.extraParam = {
        name: "Elevation",
        minValue: - max,
        maxValue: - min,
        stepSize: step,
        nameExtraParam: name,
      };

      this.extraParamExport = {
        name: "Depth",
        minValue: min,
        maxValue: max,
        stepSize: step,
        nameExtraParam: name,
      }

    }
    else {
      this.extraParam = {
        name: 'Dim_' + name,
        minValue: min,
        maxValue: max,
        stepSize: step,
        nameExtraParam: name,
      };

      this.extraParamExport = {
        name: "Dim_" + name,
        minValue: min,
        maxValue: max,
        stepSize: step,
        nameExtraParam: name,
      }
    }
    // if(this.value this.extraParam.maxValue){
    // console.log("CONSTROL EXTRA: ", controlExtra);
    this.value = controlExtra ? controlExtra : this.extraParam.maxValue.toFixed(4);

    this.options = {
      floor: this.extraParam.minValue,
      ceil: this.extraParam.maxValue,
      step: Number(this.extraParam.stepSize.toFixed(4)),
    };
    if (controlExtra) {
      this.sliderGroup.get('sliderControl')?.setValue(controlExtra);
    }
    else {
      if (name === "depth") {
        this.sliderGroup.get('sliderControl')?.setValue(this.extraParam.maxValue);
      }
      else {
        this.sliderGroup.get('sliderControl')?.setValue(this.extraParam.minValue);
      }
    }

  }

  getLayers(idMeta: any, controlDate?: any, controlExtra?: any) {

    //let d = new Date()
    // d.setUTCSeconds
    this.metadata = this.metadata["metadata"];
    // console.log("Metadata=======",this.metadata);

    // d.setUTCSeconds

    const seconds_epoch = this.metadata[0][2].split(",");

    const seconds_epoch_start = seconds_epoch[0];

    const seconds_epoch_end = seconds_epoch[1];

    const date_start = new Date(0);
    date_start.setUTCSeconds(seconds_epoch_start);
    const date_end = new Date(0);
    date_end.setUTCSeconds(seconds_epoch_end.trim());
    date_start.setHours(date_start.getHours() - 1)
    date_end.setHours(date_end.getHours() - 1)

    this.dateStart = date_start;
    this.dateEnd = date_end;

    this.dateFilter = (date: Date | null): boolean => {
      if (date) {
        if (this.selData.get("dataSetSel")?.value.name.adriaclim_timeperiod === "yearly") {
          return date.getMonth() === this.dateEnd.getMonth() &&
            date.getDate() === this.dateEnd.getDate() &&
            date.getFullYear() >= this.dateStart.getFullYear() &&
            date.getFullYear() <= this.dateEnd.getFullYear()
        }
        if (this.selData.get("dataSetSel")?.value.name.adriaclim_timeperiod === "monthly") {
          //GESTIRE ULTIMO GIORNO DEL MESE!
          const d1 = _.cloneDeep(this.dateEnd);
          if (this.isLastDayOfMonth(d1)) {
            //ULTIMO GIORNO DEL MESE CASISTICA
            //mi prendi quelli di tutti i mesi precedenti e dell'ultimo giorno
            const d2 = _.cloneDeep(date);
            if (d2 <= this.dateEnd && d2 >= this.dateStart && this.isLastDayOfMonth(d2)) {
              return true;
            } else {
              return false;
            }
          } else {
            return date.getDate() === this.dateEnd.getDate() &&
              date.getFullYear() >= this.dateStart.getFullYear() &&
              date.getFullYear() <= this.dateEnd.getFullYear()
          }
        }
        if (this.selData.get("dataSetSel")?.value.name.adriaclim_timeperiod === "seasonal") {
          //SAME DAY AND 3 MONTHS DIFFERENCE BETWEEN DAYS!
          //GESTIRE ULTIMO GIORNO DEL MESE
          const d1 = _.cloneDeep(this.dateEnd);
          if (this.isLastDayOfMonth(d1)) {
            //ULTIMO GIORNO DEL MESE CASISTICA
            //mi prendi quelli di tutte le stagioni precedenti e dell'ultimo giorno
            const d2 = _.cloneDeep(date);
            if (d2 <= this.dateEnd && d2 >= this.dateStart && ((this.dateEnd.getMonth() + 1) - (d2.getMonth() + 1)) % 3 === 0 && this.isLastDayOfMonth(d2)) {
              return true;
            } else {
              return false;
            }
          } else {
            return date.getDate() === this.dateEnd.getDate() &&
              ((this.dateEnd.getMonth() + 1) - (date.getMonth() + 1)) % 3 === 0 &&
              date.getFullYear() >= this.dateStart.getFullYear() &&
              date.getFullYear() <= this.dateEnd.getFullYear();
          }

        } else {
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
    if (controlDate === "ok") {
      const tmp = this.selectedDate.get("dateSel")?.value;
      time = this.formatDate(tmp);

    }
    else {
      this.selectedDate.get("dateSel")?.setValue(date_end);
      time = this.formatDate(date_end);
    }

    if (this.selectedDate.get("dateSel")?.value === this.dateEnd) {

      this.navigateDateLeftYear = false;
      this.navigateDateRightYear = true;
      this.navigateDateLeftMonth = false;
      this.navigateDateRightMonth = true;
      this.navigateDateLeftSeason = false;
      this.navigateDateRightSeason = true;
    }

    //se non è settata setta a this.metadata[0][4], se viene cambiata prendila da variable group
    //se cambio layer, cambiano le variabili quindi settare di nuovo a this.metadata
    if (!this.variableGroup.get("variableControl")?.value) {
      this.variableGroup.get("variableControl")?.setValue(this.metadata[0][4]);

    }

    const layer_name = this.variableGroup.get("variableControl")?.value;

    //if num_parameters.length > 3, layers3D!!!
    const num_parameters = this.metadata[0][1].split(", ");
    // console.log("NUM PARAMETERS =", num_parameters.length);

    if (this.selData.get("dataSetSel")?.value.name.wms_url === "") {

      //GESTIONE PARAMETRO AGGIUNTIVO PER I GRIDDAP SENZA WMS!!!!!
      this.getDataVectorialTabledap();

    }
    else {

      // this.legendLayer_src = this.ERDDAP_URL + "/griddap/" + idMeta + ".png?" + layer_name + "%5B(" + this.formatDate(time) + ")%5D%5B%5D%5B%5D&.legend=Only";

      if (num_parameters.length <= 3) {
        this.isExtraParam = false;
        //siamo nel caso di layers 2D!!!
        this.layer_to_attach = {
          layer_name: L.tileLayer.wms(
            this.apiUrl + 'test/layers2d', {
              attribution: this.metadata[0][6],
              bgcolor: '0x808080',
              crs: L.CRS.EPSG4326,
              format: 'image/png',
              layers: idMeta + ':' + layer_name,
              styles: '',
              time: time,
              transparent: true,
              version: '1.3.0',
              opacity: 0.7,
            } as ExtendedWMSOptions)
        };
        // console.log("NON ENTRO NEL PARAMETRO AGGIUNTIVO");

        this.legendLayer_src = this.ERDDAP_URL + "/griddap/" + idMeta + ".png?" + layer_name + "%5B(" + this.formatDate(time) + ")%5D%5B%5D%5B%5D&.legend=Only";

      } else {

        //siamo nel caso di layers 3D!!
        //di default gli assegniamo il minimo valore!
        const min_max_value = this.metadata[0][0].split(",");
        const name = num_parameters[1];
        const min = Number(min_max_value[0]);
        const max = Number(min_max_value[1]);
        const step = Number(this.metadata[0][5].split("=")[1]);
        // console.log("ENTRO NEL CASO DEL PARAMETRO AGGIUNTIVO!");
        // console.log("NOME PARAMETRO AGGIUNTIVO======",name);
        // console.log("VALORE MIN",min);
        // console.log("VALORE MAX",max);
        // console.log("STEP",step);

        //se non c'è ci sono questi due if, se c'è hai sempre
        if (name === "depth") {
          // this.extraParam.name = "elevation";
          this.extraParam = {
            name: "Elevation",
            minValue: - max,
            maxValue: - min,
            stepSize: step,
            nameExtraParam: name,
          };

          this.extraParamExport = {
            name: "Depth",
            minValue: min,
            maxValue: max,
            stepSize: step,
            nameExtraParam: name,
          }

        }
        else {
          this.extraParam = {
            name: 'Dim_' + name,
            minValue: min,
            maxValue: max,
            stepSize: step,
            nameExtraParam: name,
          };

          this.extraParamExport = {
            name: "Dim_" + name,
            minValue: min,
            maxValue: max,
            stepSize: step,
            nameExtraParam: name,
          }
        }
        // if(this.value this.extraParam.maxValue){
        // console.log("CONSTROL EXTRA: ", controlExtra);
        this.value = controlExtra ? controlExtra : this.extraParam.maxValue.toFixed(4);
        this.options = {
          floor: this.extraParam.minValue,
          ceil: this.extraParam.maxValue,
          step: Number(this.extraParam.stepSize.toFixed(4)),
        };
        if (controlExtra) {
          this.sliderGroup.get('sliderControl')?.setValue(controlExtra);

          this.layer_to_attach = {
            layer_name: L.tileLayer.wms(
              this.apiUrl + 'test/layers3d/' + this.extraParam.name, {
                attribution: this.metadata[0][6],
                bgcolor: '0x808080',
                crs: L.CRS.EPSG4326,
                format: 'image/png',
                layers: idMeta + ':' + layer_name,
                styles: '',
                time: time,
                [this.extraParam.name]: controlExtra,
                transparent: true,
                version: '1.3.0',
                opacity: 0.7,
              } as ExtendedWMSOptions)
          };

          this.isExtraParam = true;
          if (name === "depth") {
            this.legendLayer_src = this.ERDDAP_URL + "/griddap/" + idMeta + ".png?" + layer_name + "%5B(" + this.formatDate(time) + ")%5D%5B(" + (-controlExtra) + ")%5D%5B%5D%5B%5D&.legend=Only";
          } else {
            this.legendLayer_src = this.ERDDAP_URL + "/griddap/" + idMeta + ".png?" + layer_name + "%5B(" + this.formatDate(time) + ")%5D%5B(" + (controlExtra) + ")%5D%5B%5D%5B%5D&.legend=Only";
          }
        }
        else {
          if (name === "depth") {
            this.sliderGroup.get('sliderControl')?.setValue(this.extraParam.maxValue);
          }
          else {
            this.sliderGroup.get('sliderControl')?.setValue(this.extraParam.minValue);
          }

          this.layer_to_attach = {
            layer_name: L.tileLayer.wms(
              this.apiUrl + 'test/layers3d/' + this.extraParam.name, {
                attribution: this.metadata[0][6],
                bgcolor: '0x808080',
                crs: L.CRS.EPSG4326,
                format: 'image/png',
                layers: idMeta + ':' + layer_name,
                styles: '',
                time: time,
                [this.extraParam.name]: this.sliderGroup.get('sliderControl')?.value,
                transparent: true,
                version: '1.3.0',
                opacity: 0.7,
              } as ExtendedWMSOptions)
          };

          this.isExtraParam = true;
          this.legendLayer_src = this.ERDDAP_URL + "/griddap/" + idMeta + ".png?" + layer_name + "%5B(" + this.formatDate(time) + ")%5D%5B(" + this.sliderGroup.get('sliderControl')?.value + ")%5D%5B%5D%5B%5D&.legend=Only";

        }

      }
      if (this.legendLayer_src && this.datasetLayer) {
        this.map.removeLayer(this.datasetLayer);

      }
      this.datasetLayer = this.layer_to_attach.layer_name.addTo(this.map);
    }

  }

  sliderControl(event: any) {
    // console.log("EVENTO SLIDERRRRRRRRR =", event.value);

    this.valueCustom = event.value;
    let metaId: any;
    if (this.selData.get("dataSetSel")?.value.name.dataset_id) {
      metaId = this.selData.get("dataSetSel")?.value.name.dataset_id;
    }
    else if (this.selData.get("dataSetSel")?.value.name.id) {
      metaId = this.selData.get("dataSetSel")?.value.name.id;
    }
    this.getMeta(metaId, "ok", this.valueCustom);
  }

  formatLabel(value: number): string {
    if (value >= 1000) {
      return Math.round(value / 1000) + 'k';
    }

    return `${value}`;
  }

  landLayers() {

    const overlays = {
      Land: L.tileLayer.wms(
        this.apiUrl + 'test/addOverlays/atm_regional_76a1_c4ac_038a', {
          bgcolor: '0x808080',
          crs: L.CRS.EPSG4326,
          format: 'image/png',
          layers: 'Land',
          styles: '',
          transparent: true,
          version: '1.3.0'
        } as ExtendedWMSOptions
      ),
      Coastlines: L.tileLayer.wms(
        this.apiUrl + 'test/addOverlays/atm_regional_76a1_c4ac_038a', {
          bgcolor: '0x808080',
          crs: L.CRS.EPSG4326,
          format: 'image/png',
          layers: 'Coastlines',
          styles: '',
          transparent: true,
          version: '1.3.0'
        } as ExtendedWMSOptions
      ),
      LakesAndRivers: L.tileLayer.wms(
        this.apiUrl + 'test/addOverlays/atm_regional_76a1_c4ac_038a', {
          bgcolor: '0x808080',
          crs: L.CRS.EPSG4326,
          format: 'image/png',
          layers: 'LakesAndRivers',
          styles: '',
          transparent: true,
          version: '1.3.0'
        } as ExtendedWMSOptions
      ),
      Nations: L.tileLayer.wms(
        this.apiUrl + 'test/addOverlays/atm_regional_76a1_c4ac_038a', {
          bgcolor: '0x808080',
          crs: L.CRS.EPSG4326,
          format: 'image/png',
          layers: 'Nations',
          styles: '',
          transparent: true,
          version: '1.3.0'
        } as ExtendedWMSOptions
      ),
      States: L.tileLayer.wms(
        this.apiUrl + 'test/addOverlays/atm_regional_76a1_c4ac_038a', {
          bgcolor: '0x808080',
          crs: L.CRS.EPSG4326,
          format: 'image/png',
          layers: 'States',
          styles: '',
          transparent: true,
          version: '1.3.0'
        } as ExtendedWMSOptions
      )
    };

    const control_layers = L.control.layers().addTo(this.map);
    control_layers.addOverlay(overlays.Land, "Land");
    control_layers.addOverlay(overlays.Coastlines, "Coastlines");
    control_layers.addOverlay(overlays.States, "States");
    control_layers.addOverlay(overlays.Nations, "Nations");
    control_layers.addOverlay(overlays.LakesAndRivers, "LakesAndRivers");

  }

  deleteLayer(idMeta?: string) {
    let metaId: any;
    if (this.legendNoWms) {
      this.markersLayer.clearLayers();
      this.circleMarkerArray = [];
      this.circleCoords = [];
      this.rettangoliLayer.clearLayers();
      this.isIndicator = false;
      this.map.removeControl(this.legendNoWms);
    }
    if (idMeta) {
      metaId = idMeta;
    }
    else {
      if (this.selData.get("dataSetSel")?.value.name.dataset_id) {
        metaId = this.selData.get("dataSetSel")?.value.name.dataset_id;
      }
      else if (this.selData.get("dataSetSel")?.value.name.id) {
        metaId = this.selData.get("dataSetSel")?.value.name.id;
      }
    }

    if (this.legendLayer_src) {
      this.map.removeLayer(this.datasetLayer);

    }
    this.legendLayer_src = null;

  }

  deleteElActiveLayers() {

    let metaId: any;
    if (this.selData.get("dataSetSel")?.value.name.dataset_id) {
      metaId = this.selData.get("dataSetSel")?.value.name.dataset_id;
    }
    else if (this.selData.get("dataSetSel")?.value.name.id) {
      metaId = this.selData.get("dataSetSel")?.value.name.id;
    }

    this.activeLayersArray.forEach((layer: any, i: number) => {
      if (layer.name.dataset_id === metaId) {
        //rimuovi array nel caso di layer da lista dataset
        this.activeLayersArray.splice(i, 1);
      } else if (layer.name.id === metaId) {
        //rimuovi array nel caso di layer da full list
        this.activeLayersArray.splice(i, 1);
      }
    });
    if (this.activeLayersArray.length >= 1) {
      this.selData.get("dataSetSel")?.setValue(this.activeLayersArray[this.activeLayersArray.length - 1]);
      // if(this.selData.get("dataSetSel")?.value) {
      //   this.getMeta();
      // }
      if (this.selData.get("dataSetSel")?.value.name.dataset_id) {
        metaId = this.selData.get("dataSetSel")?.value.name.dataset_id;
      }
      else if (this.selData.get("dataSetSel")?.value.name.id) {
        metaId = this.selData.get("dataSetSel")?.value.name.id;
      }
      if (this.selData.get("dataSetSel")?.value.name.wms_url !== "") {

        if (this.clickPointOnOff) {
          this.map.off('click');
          this.map.on("click", this.onMapClick.bind(this));
        }

      }
      this.getSelectedNode(this.selData.get("dataSetSel")?.value);
      this.getMeta(metaId);
    }
    else {
      this.selData.reset();
      this.variableArray = [];
    }

  }

  getValuesByKey(arr: any[], key: string) {
    return arr
      .filter((dict) => dict.hasOwnProperty(key))
      .map((dict) => dict[key]);
  }

  /**
   * FUNZIONE CHE PERMETTE DI FORMATTARE OTTENENDO LA FORMATTAZIONE CORRETTA DA VISUALIZZARE
   */
  formatDate(date: any) {
    const d = new Date(date);
    let month = '' + (d.getMonth() + 1);
    let day = '' + d.getDate();
    const year = d.getFullYear();

    if (month.length < 2)
      month = '0' + month;
    if (day.length < 2)
      day = '0' + day;

    const first_part = [year, month, day].join('-');
    const second_part = "T00:00:00Z";
    return first_part + second_part;
  }

  /**
   * TREE
   */
  /** The selection for checklist */
  checklistSelection = new SelectionModel<ExampleFlatNode>(false /* multiple */);

  // typesOfShoes: string[] = ['Boots', 'Clogs', 'Loafers', 'Moccasins', 'Sneakers'];
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

  /**
   * FUNZIONE CHE APRE LA MODALE CONTENENTE LA TABELLA DEI METADATI DEL DATASET SELEZIONATO
   */
  openTableDialog(idMeta?: any, title?: any, n?: any) {
    let dataId: any;
    // console.log("ID META =", idMeta);
    // console.log("title =====",title);
    // console.log("N =", n);

    if (!idMeta) {
      if (this.selData.get("dataSetSel")?.value.name.dataset_id) {
        dataId = this.selData.get("dataSetSel")?.value.name.dataset_id;
      }
      else if (this.selData.get("dataSetSel")?.value.name.id) {
        dataId = this.selData.get("dataSetSel")?.value.name.id;
      }
    }

    const dialogConfig = new MatDialogConfig();

    dialogConfig.disableClose = true;
    dialogConfig.autoFocus = true;

    dialogConfig.data = {
      success: true,
      datasetId: idMeta ? idMeta : dataId,
      datasetName: title ? title : this.selData.get("dataSetSel")?.value.name.title,
    };
    // console.log("DIALOG CONF DATA =", dialogConfig.data);

    const dialogRef = this.dialog.open(GeoportalMapDialogComponent, dialogConfig);

  }

  /**
   * FUNZIONE CHE PERMETTE DI APRIRE LA MODALE CONTENENTE IL GRAFICO DEL DATASET SELEZIONATO
   */
  openGraphDialog(lat?: any, lng?: any, polygon?: any) {
    // console.log("SONO DENTRO OPEN GRAPH DIALOG");

    const dialogConfig = new MatDialogConfig();
    dialogConfig.disableClose = true;
    dialogConfig.autoFocus = true;

    // if (this.circleMarkerArray.length > 0) {
    //   this.circleMarkerArray.forEach((circle: any) => {
    //     circle.removeEventListener('click');
    //   });
    // }

    // if(this.confronto) {
    //   // firstDataset: this.form.get('firstDataset')?.value,
    //   // secondDataset: this.form.get('secondDataset')?.value,
    //   // firstVarSel: this.form.get('variableFirstData')?.value,
    //   // secondVarSel: this.form.get('variableSecondData')?.value,
    //   let dataId = this.datasetCompare.firstDataset.name.dataset_id;
    //   let title = this.datasetCompare.firstDataset.name.title;
    //   let firstDataset = this.datasetCompare.firstDataset;
    //   let secondDataset = this.datasetCompare.secondDataset;
    //   let firstVariable = this.datasetCompare.firstVarSel;
    //   let secondVariable = this.datasetCompare.secondVarSel;

    //   dialogConfig.data = {
    //     success: true,
    //     datasetId: dataId,
    //     datasetName: title,
    //     confronto: this.confronto,
    //     firstDataset: firstDataset,
    //     seconddataset: secondDataset,
    //     latlng: this.coordOnClick,
    //     firstVariable: firstVariable,
    //     secondVariable: secondVariable,

    //     dateStart: this.dateStart,
    //     dateEnd: this.dateEnd,

    //     // arrayVariable: this.variableArray,
    //     // range: this.value,
    //     openGraph: true,
    //     // extraParamExport: this.extraParamExport,
    //     // polyExport: polygon ? polygon[0].pol.getBounds() : null,
    //     // polygon: polygon ? polygon[0].pol.getLatLngs()[0] : null,
    //     // polName: polygon ? polygon[0].polName : null,
    //     // circleCoords: this.circleCoords,
    //     isIndicator: this.isIndicator ? "true" : "false",
    //   };

    // }
    // else {

    let dataId: any;
    if (this.selData.get("dataSetSel")?.value) {

      // CASO DATASET SELEZIONATO
      const title = this.selData.get("dataSetSel")?.value.name.title;

      if (this.selData.get("dataSetSel")?.value.name.dataset_id) {
        dataId = this.selData.get("dataSetSel")?.value.name.dataset_id;
      }
      else if (this.selData.get("dataSetSel")?.value.name.id) {
        dataId = this.selData.get("dataSetSel")?.value.name.id;

      }
      let splittedVar = this.selData.get("dataSetSel")?.value.name.variable_names.split(" ");
      splittedVar = splittedVar[splittedVar.length - 1];

      if (lat) {
        this.coordOnClick = { "lat": lat, "lng": lng };
      }

      // console.log("POLYGON =", polygon);
      dialogConfig.data = {
        success: true,
        datasetId: dataId,
        datasetName: title,
        confronto: this.confronto,
        dataset: this.selData.get("dataSetSel")?.value.name,
        latlng: this.coordOnClick,
        dateStart: this.dateStart,
        dateEnd: this.dateEnd,
        // variable: this.selData.get("dataSetSel")?.value.name.griddap_url !== "" ? this.variableGroup.get("variableControl")?.value : splittedVar,
        variable: this.variableGroup.get("variableControl")?.value,
        arrayVariable: this.getValuesByKey(this.variableArray, "name"),
        range: this.isExtraParam ? this.value : 0,
        openGraph: true,
        extraParamExport: this.isExtraParam ? this.extraParamExport : null,
        polyExport: polygon ? polygon[0].pol.getBounds() : null,
        polygon: polygon ? polygon[0].pol.getLatLngs()[0] : null,
        polName: polygon ? polygon[0].polName : null,
        circleCoords: this.circleCoords,
        isIndicator: this.isIndicator ? "true" : "false",
      };

      // console.log("RANGE =", this.value);
      // console.log("EXTRA PARAM EXPORT =", this.extraParamExport);

    }
    else {
      //CASO DATASET NON SELEZIONATO
      dialogConfig.data = {
        success: true,
        description: "Select a dataset to visualize the graph",
        openGraph: true,
      };
    }
    // console.log("DATASET COMPARE =", this.datasetCompare);

    if (this.datasetCompare != null && this.compare) {
      this.compareObj = {
        firstDataset: this.datasetCompare.firstDataset,
        firstVarSel: this.datasetCompare.firstVarSel,
        firstValue: + this.datasetCompare.firstValue,
        secondDataset: this.datasetCompare.secondDataset,
        secondVarSel: this.datasetCompare.secondVarSel,
        secondValue: + this.datasetCompare.secondValue,
        latlng: this.coordOnClick,
        compare: this.compare,
      }
      dialogConfig.data["compareObj"] = this.compareObj;
      this.compare = false;
      this.datasetCompare = null;
    }
    // console.log("DIALOG CONFIG DATA =", dialogConfig.data);

    // }

    const dialogRef = this.dialog.open(GeoportalMapDialogComponent, dialogConfig);

  }

  openSnackBar(message: string, action: string, horizontal: MatSnackBarHorizontalPosition, vertical: MatSnackBarVerticalPosition) {
    this._snackBar.open(message, action, {
      horizontalPosition: horizontal,
      verticalPosition: vertical,
    });
  }

  /**
   * PRENDIAMO I DATI DEL DATASET TABLEDAP SELEZIONATO
   */
  getDataVectorialTabledap() {

    let splittedVar = this.selData.get("dataSetSel")?.value.name.variable_names.split(" ");
    splittedVar = splittedVar[splittedVar.length - 1];
    //se isIndicator è true, allora si tratta di un tabledap, altrimenti è griddap
    this.isIndicator = this.selData.get("dataSetSel")?.value.name.griddap_url !== "" ? false : true;
    if (this.isIndicator) {
      //è un tabledap quindi niente extra param
      this.isExtraParam = false;
    } else {
      //è un griddap
      if (this.selData.get("dataSetSel")?.value.name.dimensions > 3) {

        this.isExtraParam = true;
        this.extraParamNoWms(this.metadata, this.valueCustom);
      } else {
        this.isExtraParam = false;
      }
    }
    this.httpService.post('test/dataVectorial', {
      dataset: this.selData.get("dataSetSel")?.value.name,
      // selVar: this.selData.get("dataSetSel")?.value.name.griddap_url !== "" ? this.variableGroup.get("variableControl")?.value : splittedVar,
      selVar: this.variableGroup.get("variableControl")?.value,
      isIndicator: this.isIndicator ? "true" : "false",
      selDate: this.formatDate(this.selectedDate.get("dateSel")?.value),
    }).subscribe({
      next: (res: any) => {
        // console.log("RES =", res);
        if(res.dataVect.includes("HTTP Error 404")) {
          this.compliantErrorErddap = "The data is not compliant"
          // console.log("ERR =", this.compliantErrorErddap);

          // Alert tramite bootstrap con html
          this.showAlert = true;

          // Alert tramite snackBar angular material
          // this.openSnackBar("The data is not compliant", "Close", "center", "top");

        }
        else {

          this.allDataVectorial = res['dataVect'];
          let allLatCoordinates = this.allDataVectorial[1];
          let allLongCoordinates = this.allDataVectorial[2];
          let allValues = this.allDataVectorial[0];
          let value_min = this.allDataVectorial[3];
          let value_max = this.allDataVectorial[4];
          let bounds: any;
          let rectangle: any;
          let value_mid: any;
          if (parseFloat(value_min) < 0) {
            value_mid = Math.ceil((parseFloat(value_max) - parseFloat(value_min)) / 2);
          } else {
            value_mid = Math.ceil((parseFloat(value_max) + parseFloat(value_min)) / 2);
          }
          this.valueMin = parseFloat(value_min);
          this.valueMax = parseFloat(value_max);
          this.valueMid = value_mid;

          this.createLegend(parseFloat(value_min), parseFloat(value_max), value_mid);
          // this.markersLayer = L.layerGroup();
          // markersLayer: L.LayerGroup = L.layerGroup();
          let centerLat;
          let centerLong;
          if (allLatCoordinates.length === 1) {
            centerLat = allLatCoordinates[0];
            centerLong = allLongCoordinates[0];

          } else {
            const center = Math.round(allLatCoordinates.length / 2);
            // console.log("Center",center);
            centerLat = allLatCoordinates[center];
            centerLong = allLongCoordinates[center];
          }

          // console.log("centerlat",centerLat);
          // console.log("centerlng",centerLong);
          const zoomTest = L.latLng(centerLat, centerLong);
          if (allLatCoordinates.length === 1) {
            // zoom più elevato essendo un singolo punto!
            this.map.setView(zoomTest, 14);
          } else {
            this.map.setView(zoomTest, 8);
          }

          for (let i = 0; i < allLatCoordinates.length; i++) {
            if (this.isIndicator) {
              this.circleCoords.push(
                {
                  lat: allLatCoordinates[i],
                  lng: allLongCoordinates[i],
                }
              )
              // console.log("this.circleCoords.push",this.circleCoords);
              //tabledap case, with circle
              const colorStorage = localStorage.getItem(this.selData.get("dataSetSel")?.value.name.title);
              let varColor: any;
              if (colorStorage) {
                const colorStorageJson = JSON.parse(colorStorage);
                varColor = this.getColor(allValues[i], value_min, value_max, colorStorageJson.minColor, colorStorageJson.midColor, colorStorageJson.maxColor);
              } else {
                varColor = this.getColor(allValues[i], value_min, value_max, "#f44336", "#9c27b0", "#3f51b5");
              }
              this.markerToAdd = L.circleMarker([parseFloat(allLatCoordinates[i]), parseFloat(allLongCoordinates[i])], { radius: 15, weight: 2, color: this.fillRectangleColor(varColor.r, varColor.g, varColor.b) });
              this.circleMarkerArray.push(this.markerToAdd);
              this.markersLayer.addLayer(this.markerToAdd);


              this.map.addLayer(this.markersLayer);

            } else {
              //griddap case with rectangle, NON SERVONO I MARKER!

              bounds = [[parseFloat(allLatCoordinates[i]) - 0.005001, parseFloat(allLongCoordinates[i]) - 0.0065387], [parseFloat(allLatCoordinates[i]) + 0.005001, parseFloat(allLongCoordinates[i]) + 0.0065387]];
              let colorStorage = localStorage.getItem(this.selData.get("dataSetSel")?.value.name.title);
              let varColor: any;
              if (colorStorage) {
                let colorStorageJson = JSON.parse(colorStorage);
                varColor = this.getColor(allValues[i], value_min, value_max, colorStorageJson.minColor, colorStorageJson.midColor, colorStorageJson.maxColor);

              }
              else {
                varColor = this.getColor(allValues[i], value_min, value_max, "#f44336", "#9c27b0", "#3f51b5");

              }

              // let rectangle = L.rectangle(bounds, { fillOpacity: 0.8, opacity: 0.8, fill: true, stroke: false, color: this.fillRectangleColor(varColor.r, varColor.g, varColor.b), weight: 1 }).bindTooltip(allValues[i]);
              let rectangle = L.rectangle(bounds, { fillOpacity: 0.8, opacity: 0.8, fill: true, stroke: false, color: this.fillRectangleColor(varColor.r, varColor.g, varColor.b), weight: 1 });
              this.rettangoliLayer.addLayer(rectangle);

              this.map.addLayer(this.rettangoliLayer);

            }
          }
          if (this.circleMarkerArray.length > 0 && this.clickPointOnOff) {
            this.circleMarkerArray.forEach((circle: any) => {
              circle.addEventListener('click', (e: any) => this.openGraphDialog(circle.getLatLng().lat, circle.getLatLng().lng));
            });
            this.map.off('click');
          }
        }

      },
      error: (msg: any) => {
        console.log('METADATA ERROR: ', msg);
      }

    });
  }

  //function to fill the color of the rectangles of vectorial layer
  fillRectangleColor(r: any, g: any, b: any) {
    return "rgb(" + r + "," + g + "," + b + ")";
  }
  hexToRgb(hex: any) {
    // Expand shorthand form (e.g. "03F") to full form (e.g. "0033FF")
    const shorthandRegex = /^#?([a-f\d])([a-f\d])([a-f\d])$/i;
    hex = hex.replace(shorthandRegex, function (m: any, r: any, g: any, b: any) {
      return r + r + g + g + b + b;
    });

    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? {
      r: parseInt(result[1], 16),
      g: parseInt(result[2], 16),
      b: parseInt(result[3], 16)
    } : null;
  }

  getColor(v: any, min: any, max: any, colorMin: any, colorMid: any, colorMax: any) {

    function getC(f: any, l: any, r: any) {
      return {
        r: Math.floor((1 - f) * l.r + f * r.r),
        g: Math.floor((1 - f) * l.g + f * r.g),
        b: Math.floor((1 - f) * l.b + f * r.b),
      };
    }
    let left: any,
      middle: any,
      right: any,
      mid: any;
    if (colorMin === "") {
      left = { r: 0, g: 0, b: 255 },
        middle = { r: 255, g: 255, b: 0 },
        right = { r: 255, g: 0, b: 0 },
        mid = (max - min) / 2;
    } else {
      left = { r: this.hexToRgb(colorMin)?.r, g: this.hexToRgb(colorMin)?.g, b: this.hexToRgb(colorMin)?.b },
        middle = { r: this.hexToRgb(colorMid)?.r, g: this.hexToRgb(colorMid)?.g, b: this.hexToRgb(colorMid)?.b },
        right = { r: this.hexToRgb(colorMax)?.r, g: this.hexToRgb(colorMax)?.g, b: this.hexToRgb(colorMax)?.b },
        mid = (max - min) / 2;
    }
    return v < min + mid ?
      getC((v - min) / mid, left, middle) :
      getC((v - min - mid) / mid, middle, right);
  }

  /**
   * FUNZIONE CHE PERMETTE DI RIPRISTINARE I COLORI DI DEFAULT DELLA LEGENDA
   */
  restoreDefaultColors() {
    this.valueMinColor = this.valueMinColorDefault;
    this.valueMidColor = this.valueMidColorDefault;
    this.valueMaxColor = this.valueMaxColorDefault;
    this.valueMinMidColor = this.valueMinMidColorDefault;
    this.valueMidMaxColor = this.valueMidMaxColorDefault;

  }

  // CREIAMO LA LEGENDA PER I NO WMS
  createLegend(value_min: any, value_max: any, value_mid: any) {
    let value_min_mid: any;
    let value_mid_max: any;
    this.legendNoWms = new L.Control({ position: "bottomleft" });
    if (parseFloat(value_min) < 0) {

      value_min_mid = Math.ceil((parseFloat(value_mid) - parseFloat(value_min)) / 2);
      value_mid_max = Math.ceil((parseFloat(value_max) - parseFloat(value_mid)) / 2);
    }
    else {
      value_min_mid = Math.ceil((parseFloat(value_mid) + parseFloat(value_min)) / 2);
      value_mid_max = Math.ceil((parseFloat(value_max) + parseFloat(value_mid)) / 2);
    }
    // console.log("VALUE MIN =", value_min);
    // console.log("VALUE MIN MID =", value_min_mid);
    // console.log("VALUE MID =", value_mid);
    // console.log("VALUE MID MAX =", value_mid_max);
    // console.log("VALUE MAX =", value_max);

    value_min = this.formatNumber(value_min, 5);
    value_min_mid = this.formatNumber(value_min_mid, 5);
    value_mid = this.formatNumber(value_mid, 5);
    value_mid_max = this.formatNumber(value_mid_max, 5);
    value_max = this.formatNumber(value_max, 5);

    const getColor = (v: any) => {
      const colorStorage = localStorage.getItem(this.selData.get("dataSetSel")?.value.name.title);
      let colorStorageObj: any;
      if (colorStorage) {
        // console.log("Entro nell'if del localstorage COLOR,this is ", colorStorage);
        colorStorageObj = JSON.parse(colorStorage);
        return v === value_min
          ? colorStorageObj?.minColor
          : v === value_min_mid
            ? colorStorageObj?.minMidColor
            : v === value_mid
              ? colorStorageObj?.midColor
              : v === value_mid_max
                ? colorStorageObj?.midMaxColor
                : v === value_max
                  ? colorStorageObj?.maxColor
                  : colorStorageObj?.maxColor;

      }
      else {
        // console.log("Entro nell'else del localstorage COLOR,this is valueMinColor ",this.valueMinColor);
        this.restoreDefaultColors();
        return v === value_min
          ? this.valueMinColor
          : v === value_min_mid
            ? this.valueMinMidColor
            : v === value_mid
              ? this.valueMidColor
              : v === value_mid_max
                ? this.valueMidMaxColor
                : v === value_max
                  ? this.valueMaxColor
                  : this.valueMaxColor;
      }
    }

    this.legendNoWms.onAdd = (map: any) => {
      const div = L.DomUtil.create('div', 'info legend');
      const grades = [value_min, value_min_mid, value_mid, value_mid_max, value_max];
      const labels = [];
      let from: any;
      let to: any;

      for (let i = 0; i < grades.length; i++) {
        from = grades[i];
        to = grades[i + 1];

        labels.push(
          "<div class='color-number-legend'>" + '<i style="background:' + getColor(from) + '; margin-right: 10px;"></i> ' +
          "<span>" + from + (to ? '&ndash;' + to : "") + "</span>" + "</div>"
        );
      }
      const button = L.DomUtil.create('button', 'color-number-legend');
      button.innerHTML = `<span class='material-symbols-outlined'>settings</span>`;
      button.addEventListener('click', (e) => this.changeLegendColors());

      div.innerHTML = labels.join('');
      div.appendChild(button);
      return div;
    };

    this.legendNoWms.addTo(this.map);

  }

  /**
   * FUNZIONE CHE PERMETTE DI APRIRE LA MODALE PER IL CONFRONTO TRA DUE DATASET
   */
  compareDialogModal = () => {
    this.clickPointOnOff = true;
    const dialogConfig = new MatDialogConfig();

    dialogConfig.disableClose = true;
    dialogConfig.autoFocus = true;
    //dobbiamo passargli la lista dei layers attivi!
    // console.log("this.activeLayersArray =", this.activeLayersArray);

    dialogConfig.data = {
      activeLayersArray: this.activeLayersArray,
    };

    const dialogRef = this.dialog.open(GeoportalCompareDialogComponent, dialogConfig);
    //prendere i due layers selezionati!
    dialogRef.afterClosed().subscribe(async result => {
      if (result != "") {
        // console.log("result =", result);
        this.datasetCompare = result;
        this.confronto = true;
        this.compare = true;
        // console.log("this.datasetCompare =", this.datasetCompare);
        this.pointSelect();

      }
    })

  }

  /**
   * FUNZIONE CHE PERMETTE DI CAMBIARE I COLORI DELLA LEGENDA
   */
  changeLegendColors = (title?: string) => {

    const dialogConfig = new MatDialogConfig();

    dialogConfig.disableClose = true;
    dialogConfig.autoFocus = true;

    dialogConfig.data = {
      success: true,
      openGraph: true,
      valueMinColor: this.valueMinColor,
      valueMinMidColor: this.valueMinMidColor,
      valueMidMaxColor: this.valueMidMaxColor,
      valueMidColor: this.valueMidColor,
      valueMaxColor: this.valueMaxColor,
      datasetName: this.selData.get("dataSetSel")?.value ? this.selData.get("dataSetSel")?.value.name.title : title,
    };


    const dialogRef = this.dialog.open(GeoportalColorDialogComponent, dialogConfig);
    dialogRef.afterClosed().subscribe(async result => {
      if (result !== '' && result !== "restoreDefault") {
        // eslint-disable-next-line @typescript-eslint/no-unused-vars
        const colorStorage = localStorage.getItem(this.selData.get("dataSetSel")?.value.name.title)
        this.valueMinColor = result["minColor"];
        this.valueMinMidColor = result["minMidColor"];
        this.valueMidColor = result["midColor"];
        this.valueMidMaxColor = result["midMaxColor"];
        this.valueMaxColor = result["maxColor"];

        this.map.removeControl(this.legendNoWms);
        this.createLegend(this.valueMin, this.valueMax, this.valueMid);
        //cambiare coloriCircleMarker o rettangoli
        //basta farlo chiamando clearLayers()
        if (this.isIndicator) {
          //circleMarker da rimuovere
          this.markersLayer.clearLayers();
          this.circleMarkerArray = [];
          this.circleCoords = [];
          const allLatCoordinates = this.allDataVectorial[1];
          const allLongCoordinates = this.allDataVectorial[2];
          const allValues = this.allDataVectorial[0];
          const value_min = this.allDataVectorial[3];
          const value_max = this.allDataVectorial[4];
          //aggiungere quelli nuovi
          for (let i = 0; i < allLatCoordinates.length; i++) {
            const varColor = this.getColor(allValues[i], value_min, value_max, this.valueMinColor, this.valueMidColor, this.valueMaxColor);
            this.markerToAdd = L.circleMarker([parseFloat(allLatCoordinates[i]), parseFloat(allLongCoordinates[i])], { radius: 15, weight: 2, color: this.fillRectangleColor(varColor.r, varColor.g, varColor.b) });
            this.circleMarkerArray.push(this.markerToAdd);
            this.markersLayer.addLayer(this.markerToAdd);
          }

          if (this.circleMarkerArray.length > 0 && this.clickPointOnOff) {
            this.circleMarkerArray.forEach((circle: any) => {
              circle.addEventListener('click', (e: any) => this.openGraphDialog(circle.getLatLng().lat, circle.getLatLng().lng));
            });
            this.map.off('click');
          }

        } else {
          //rectangle da rimuovere
          this.rettangoliLayer.clearLayers();
          //aggiungere quelli nuovi
          const allLatCoordinates = this.allDataVectorial[1];
          const allLongCoordinates = this.allDataVectorial[2];
          const allValues = this.allDataVectorial[0];
          const value_min = this.allDataVectorial[3];
          const value_max = this.allDataVectorial[4];
          let bounds: any;
          //aggiungere quelli nuovi
          for (let i = 0; i < allLatCoordinates.length; i++) {
            bounds = [[parseFloat(allLatCoordinates[i]) - 0.005001, parseFloat(allLongCoordinates[i]) - 0.0065387], [parseFloat(allLatCoordinates[i]) + 0.005001, parseFloat(allLongCoordinates[i]) + 0.0065387]];
            const varColor = this.getColor(allValues[i], value_min, value_max, this.valueMinColor, this.valueMidColor, this.valueMaxColor);

            const rectangle = L.rectangle(bounds, { fillOpacity: .4, opacity: .4, fill: true, stroke: false, color: this.fillRectangleColor(varColor.r, varColor.g, varColor.b), weight: 1 }).bindTooltip(allValues[i]);
            this.rettangoliLayer.addLayer(rectangle);
            this.map.addLayer(this.rettangoliLayer);
          }

        }

        // console.log("RESULT =", result);
      }
      else if (result === "restoreDefault") {
        this.restoreDefaultColors();
        if (localStorage.getItem(this.selData.get("dataSetSel")?.value.name.title)) {
          localStorage.removeItem(this.selData.get("dataSetSel")?.value.name.title);

        }
        this.map.removeControl(this.legendNoWms);
        this.createLegend(this.valueMin, this.valueMax, this.valueMid);
        if (this.isIndicator) {
          //circleMarker da rimuovere
          this.markersLayer.clearLayers();
          this.circleMarkerArray = [];
          this.circleCoords = [];
          const allLatCoordinates = this.allDataVectorial[1];
          const allLongCoordinates = this.allDataVectorial[2];
          const allValues = this.allDataVectorial[0];
          const value_min = this.allDataVectorial[3];
          const value_max = this.allDataVectorial[4];
          //aggiungere quelli nuovi
          for (let i = 0; i < allLatCoordinates.length; i++) {
            const varColor = this.getColor(allValues[i], value_min, value_max, this.valueMinColor, this.valueMidColor, this.valueMaxColor);
            this.markerToAdd = L.circleMarker([parseFloat(allLatCoordinates[i]), parseFloat(allLongCoordinates[i])], { radius: 15, weight: 2, color: this.fillRectangleColor(varColor.r, varColor.g, varColor.b) });
            this.circleMarkerArray.push(this.markerToAdd);
            this.markersLayer.addLayer(this.markerToAdd);
          }
          if (this.circleMarkerArray.length > 0 && this.clickPointOnOff) {
            this.circleMarkerArray.forEach((circle: any) => {
              circle.addEventListener('click', (e: any) => this.openGraphDialog(circle.getLatLng().lat, circle.getLatLng().lng));
            });
            this.map.off('click');
          }

        } else {
          //rectangle da rimuovere
          this.rettangoliLayer.clearLayers();
          //aggiungere quelli nuovi
          const allLatCoordinates = this.allDataVectorial[1];
          const allLongCoordinates = this.allDataVectorial[2];
          const allValues = this.allDataVectorial[0];
          const value_min = this.allDataVectorial[3];
          const value_max = this.allDataVectorial[4];
          let bounds: any;
          //aggiungere quelli nuovi
          for (let i = 0; i < allLatCoordinates.length; i++) {
            bounds = [[parseFloat(allLatCoordinates[i]) - 0.005001, parseFloat(allLongCoordinates[i]) - 0.0065387], [parseFloat(allLatCoordinates[i]) + 0.005001, parseFloat(allLongCoordinates[i]) + 0.0065387]];
            const varColor = this.getColor(allValues[i], value_min, value_max, this.valueMinColor, this.valueMidColor, this.valueMaxColor);

            // const rectangle = L.rectangle(bounds, { fillOpacity: .4, opacity: .4, fill: true, stroke: false, color: this.fillRectangleColor(varColor.r, varColor.g, varColor.b), weight: 1 }).bindTooltip(allValues[i])
            const rectangle = L.rectangle(bounds, { fillOpacity: .4, opacity: .4, fill: true, stroke: false, color: this.fillRectangleColor(varColor.r, varColor.g, varColor.b), weight: 1 });
              // .bindTooltip(allValues[i]);
            this.rettangoliLayer.addLayer(rectangle);
            this.map.addLayer(this.rettangoliLayer);
          }
        }
      }
      //this.createLegend(this.valueMin, this.valueMax, this.valueMid);
    });

  }

  /**
   *  FILTRO PER TREE CON LISTA AL POSTO DEL TREE
   */
  applyFilter(filterValue: string): any[] {
    if (filterValue) {

      filterValue = filterValue.trim().toLowerCase();
    }
    let treeFiltrato: any[] = [];
    this.dataAllNodesTree.data = TREE_DATA;

    if (this.treeControl.dataNodes) {
      if (this.treeControl.dataNodes.length > 0) {
        treeFiltrato = this.treeControl.dataNodes.filter((item: any) => {
          if (typeof item.name === "object") {

            return item.name.title.toLowerCase().includes(filterValue) || item.name.institution.toLowerCase().includes(filterValue);
          }

        })
        // console.log("TREE FILTRATO =", treeFiltrato);

      }
    }
    // if (treeFiltrato.length === 0) {
    if (!filterValue) {
      return this.dataAllNodesTree.data;
    }
    else {
      return this.dataAllNodesTree.data = treeFiltrato;
    }
  }

  formatNumber(number: any, fix: number) {
    const decimalCount = (number.toString().split('.')[1] || '').length;

    if (decimalCount > fix) {
      const fixed = number.toFixed(fix);

      return fixed;
    }

    return number.toString();
  }

  /**
   *  APPLY FILTER CON EXPAND DA RIVEDERE
   */
  // applyFilter(filterValue: string): any[] {
  //   // console.log();
  //   // console.log();
  //   // console.log();
  //   // console.log();


  //   // this.treeControl.collapseAll();
  //   // this.treeControl.expandAll();

  //   filterValue = filterValue.trim().toLowerCase();
  //   console.log("FILTER VALUE =", filterValue);
  //   let arr: any[] = [];
  //   let treeFiltrato: any[] = [];
  //   let treeClone: any;
  //   const dataClone = _.cloneDeep(this.dataAllNodesTree);
  //   if(this.treeControl.dataNodes) {
  //     if(this.treeControl.dataNodes.length > 0) {
  //       treeFiltrato = this.treeControl.dataNodes.filter((item: any) => {
  //         if(typeof item.name === "object") {

  //           return item.name.title.toLowerCase().includes(filterValue) || item.name.institution.toLowerCase().includes(filterValue);
  //         }
  //         // console.log("============================================");
  //         // console.log("============================================");
  //         // console.log("ITEM APPLY FILTER =", item);
  //         // console.log("ITEM TYPE =", typeof item);
  //         // console.log("ITEM.NAME =", item.name);
  //         // console.log("ITEM.NAME TYPE =", typeof item.name);
  //         // console.log("============================================");
  //         // console.log("============================================");
  //         // if(typeof item.name === "object") {
  //         //   console.log("INCLUDES NAME FILTER VALUE =", item.name.title.toLowerCase().includes(filterValue));
  //         //   if(item.name.title.toLowerCase().includes(filterValue) || item.name.institution.toLowerCase().includes(filterValue)) {
  //         //     // arr.push(item);
  //         //     // console.log("ARR =", arr);
  //         //     //return arr;
  //         //   }
  //         //   // return arr

  //         // }


  //       })
  //       // console.log("TREE FILTRATO =", treeFiltrato);

  //     }
  //     const numeri = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
  //     const numeriFiltrati = numeri.filter((item: any) => {
  //       return item > 5;
  //     });
  //     // console.log("NUMERI FILTRATI =", numeriFiltrati);
  //     treeClone = _.cloneDeep(this.treeControl);
  //     treeClone.dataNodes = treeFiltrato;

  //   }

  // //  dataClone = _.cloneDeep(this.dataAllNodesTree);
  //  console.log("TREE CONTROL =", this.treeControl);
  //  //  console.log("ARR =", arr);
  //  if(!filterValue) {
  //   console.log("COLLAPSE");

  //   // this.treeControl.collapseAll();
  //   // this.dataAllNodesTree = dataClone;
  //   return this.dataAllNodesTree.data;
  //   //  this.dataAllNodesTree.data = arr;
  //   // this.dataAllNodesTree.data = treeFiltrato
  //   // return this.dataAllNodesTree.data;
  // }
  // else {
  //   console.log("EXPAND");
  //   // this.treeControl.dataNodes.forEach(tree => {
  //     //   treeFiltrato.forEach(f => {
  //       //     if(tree === f) {
  //   //       tree = f;

  //   //     }
  //   //   });
  //   // });
  //   this.dataAllNodesTree.data = treeFiltrato;
  //   // this.treeControl.expandAll();
  //   // this.treeControl.dataNodes = treeFiltrato;
  //   console.log("DATA ALL NODES TREE =", this.dataAllNodesTree.data);
  //   this.dataAllNodesTree.data.forEach(element => {
  //     this.treeControl.dataNodes.forEach(tree => {
  //       if(element.name === tree.name) {
  //         if(tree.expandable === true) {
  //           this.treeControl.expand(tree);
  //         }
  //       }

  //     });
  //     // this.treeControl.expand(element)
  //   });
  //   return this.dataAllNodesTree.data;
  //   // return this.treeControl.dataNodes
  //     // this.treeControl.dataNodes.forEach(element => {

  //     // });
  //     // this.dataAllNodesTree.data = arr;
  //     // this.dataAllNodesTree.data
  //     // return this.dataAllNodesTree.data;
  //   }

  //   // this.treeControl.dataNodes = arr;
  //   // return this.dataAllNodesTree.data


  // }
  /**
   * Funzione che controlla quale bottone è stato cliccato aprendo e chiudendo il menu corrispondente
   */
  checkExpand(collapse: string) {
    if (collapse === "first") {
      this.isExpandedFirst = !this.isExpandedFirst;
      if(this.isExpandedFirst) {
        this.isExpandedSecond = false;
        this.isExpandedThird = false;
        this.isExpandedFourth = false;
      }
    }
    else if(collapse === "second") {
      this.isExpandedSecond = !this.isExpandedSecond;
      if(this.isExpandedSecond) {
        this.isExpandedFirst = false;
        this.isExpandedThird = false;
        this.isExpandedFourth = false;
      }
    }
    else if(collapse === "third") {
      this.isExpandedThird = !this.isExpandedThird;
      if(this.isExpandedThird) {
        this.isExpandedFirst = false;
        this.isExpandedSecond = false;
        this.isExpandedFourth = false;
      }
    }
    else if(collapse === "fourth") {
      this.isExpandedFourth = !this.isExpandedFourth;
      if(this.isExpandedFourth) {
        this.isExpandedFirst = false;
        this.isExpandedSecond = false;
        this.isExpandedThird = false;
      }
    }
  }

  /**
   * Funziona che cambia dinamicamente gli elementi all'interno dei vari menu
   */
  changeSel(sel?: any, type?: string) {
    console.log("PROVA FUNZIONE SEL =", sel);

    let tmpScale: any[] = [];
    let tmpTimeperiods: any[] = [];

    if(type === "c") {

      this.resAllNodes.forEach((el: any) => {
        if(el.adriaclim_dataset === this.formMenuDatasets.get("category")?.value) {
          tmpScale.push(el.adriaclim_scale);
        }
      });
      this.scaleDatasets = [...new Set(tmpScale)];
      this.formMenuDatasets.get("scale")?.setValue(this.scaleDatasets[0]);

      this.resAllNodes.forEach((el: any) => {
        if (el.adriaclim_dataset === this.formMenuDatasets.get("category")?.value && el.adriaclim_scale === this.formMenuDatasets.get("scale")?.value) {
          tmpTimeperiods.push(el.adriaclim_timeperiod);
        }
      });
      this.timeperiodDatasets = [...new Set(tmpTimeperiods)];
      this.formMenuDatasets.get("timeperiod")?.setValue(this.timeperiodDatasets[0]);

      this.menuDatasets = this.resAllNodes.filter((el: any) => el.adriaclim_dataset === this.formMenuDatasets.get("category")?.value && el.adriaclim_scale === this.formMenuDatasets.get("scale")?.value && el.adriaclim_timeperiod === this.formMenuDatasets.get("timeperiod")?.value);

    }
    else if(type === "s") {
      this.resAllNodes.forEach((el: any) => {
        if (el.adriaclim_dataset === this.formMenuDatasets.get("category")?.value && el.adriaclim_scale === this.formMenuDatasets.get("scale")?.value) {
          tmpTimeperiods.push(el.adriaclim_timeperiod);
        }
      });
      this.timeperiodDatasets = [...new Set(tmpTimeperiods)];
      this.formMenuDatasets.get("timeperiod")?.setValue(this.timeperiodDatasets[0]);

    }
    else if(type === "t") {
      this.menuDatasets = this.resAllNodes.filter((el: any) => el.adriaclim_dataset === this.formMenuDatasets.get("category")?.value && el.adriaclim_scale === this.formMenuDatasets.get("scale")?.value && el.adriaclim_timeperiod === this.formMenuDatasets.get("timeperiod")?.value);
    }

  }

  /**
   * Funzione che carica il layer corrispondente sulla mappa alla selezione di un dataset
   */
  selDatasetProva(node: any) {
    // console.log("NODE PROVA NUOVO MENU =", node);
    let obj = {
      name: node
    }

    this.getMeta(obj.name.id);
    this.addToActiveLayers(obj);
    this.getSelectedNode(obj);

  }

}
