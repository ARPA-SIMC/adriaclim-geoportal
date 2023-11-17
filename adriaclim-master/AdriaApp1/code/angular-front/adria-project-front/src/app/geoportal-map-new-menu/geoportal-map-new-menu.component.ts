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
import { GeoportalMapMenuDialogComponent } from './geoportal-map-menu-dialog/geoportal-map-menu-dialog.component';
import { SpinnerLoaderService } from '../services/spinner-loader.service';

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

interface SelPolygon {
  openAlert: boolean;
  text: string;
}

@Component({
  selector: 'app-geoportal-map-new-menu',
  templateUrl: './geoportal-map-new-menu.component.html',
  styleUrls: ['./geoportal-map-new-menu.component.scss'],
  providers: [
    {
      provide: MAT_SELECT_CONFIG,
      useValue: { overlayPanelClass: "select-overlay-pane" }
    }
  ]
})
export class GeoportalMapNewMenuComponent {

  resultMenuDialog: any;

  alertSelectPolygon: SelPolygon = {
    openAlert: false,
    text: ""
  };

  showAlertGenericError = false;
  errorMsgUploadGeojson = "";
  showAlertUploadGeojson = false;
  highlightedPolygon: any;

  allLegendsNoWms: any[] = [];
  allRectangles: any[] = [];
  sameColor = false;

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

  constructor(private httpClient: HttpClient, private dialog: MatDialog, private httpService: HttpService, private _snackBar: MatSnackBar, private fb: FormBuilder, private spinnerLoader: SpinnerLoaderService) {

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

        // Aggiungo un evento per il mouseover al poligono per cambiare il colore del bordo
        pol.on('mouseover', () => {
          pol.setStyle({ color: 'red' }); // Ripristino il colore del bordo
          this.highlightedPolygon = {
            "pol": pol,
            "polName": f.properties.popupContent
          };

        });

        // Aggiungo un evento per il mouseout al poligono per ripristinare il colore del bordo iniziale
        pol.on('mouseout', () => {
          pol.setStyle({ color: 'rgb(51, 136, 255)' }); // Cambio il colore del bordo al passaggio del mouse
          this.highlightedPolygon = null;
        });

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
   * Funzione che rimuove tutti i poligoni dalla mappa
   */
  removeAllPolygons() {

    this.allPolygons.forEach(p => {
      this.map.removeLayer(p.pol);
    })
    this.allPolygons = [];
  }

  /**
   * Funzione che rimuove i poligoni dalla mappa e aggiunge l'area adriatica
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
   * Funzione che mostra i poligoni precedentemente configurati sulla mappa
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
   * Metodo che mostra i dati del poligono caricato e selezionato
   */
  uploadGeo(): Promise<File> {

    return new Promise((resolve, reject) => {
      const input = document.createElement('input');
      input.type = 'file';
      input.accept = ['.geojson', '.json'].join(',');
      input.addEventListener('change', () => {
        const file = input.files?.[0];
        if (file) {
          console.log("FILE =", file);

          if (file.type !== 'application/json' && !file.name.includes('.geojson')) {
            this.errorMsgUploadGeojson = "Invalid file type";
            this.showAlertUploadGeojson = true;
            reject(new Error('Invalid file type'));
          }
          else {
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

                let pol = L.polygon(polyg[0]).addTo(this.map);
                // Aggiungo un evento per il mouseover al poligono per cambiare il colore del bordo
                pol.on('mouseover', () => {
                  pol.setStyle({ color: 'red' }); // Ripristino il colore del bordo
                  this.highlightedPolygon = {
                    "pol": pol,
                    "polName": f.properties.popupContent
                  };
                });

                // Aggiungo un evento per il mouseout al poligono per ripristinare il colore del bordo iniziale
                pol.on('mouseout', () => {
                  pol.setStyle({ color: 'rgb(51, 136, 255)' }); // Cambio il colore del bordo al passaggio del mouse
                  this.highlightedPolygon = null;
                });

                this.allPolygons.push({
                  "pol": pol,
                  "polName": f.properties.popupContent
                });
                polyg = [];
              });
            }

            reader.readAsText(file);

          }

        } else {
          this.errorMsgUploadGeojson = "No file chosen";
          this.showAlertUploadGeojson = true;
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
   * Metodo che apre la modale dove inserire le coordinate
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
    dialogRef.afterClosed().subscribe(async result => {
      if (result != "") {
        this.pointSelect(result.lat, result.lng);

      }
    })
  }

  /**
   * Funzione che permette di aprire la modale con il grafico corrispondente al punto cliccato all'interno del dataset sulla mappa
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
        circle.addEventListener('click', (e: any) => {

          this.openGraphDialog(circle.getLatLng().lat, circle.getLatLng().lng)
        });
      });
      this.map.off("click");
      // this.clickPointOnOff = false;
    }
    else {

      if (this.selectCoords) {

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
   * Funzione che permette di aprire la modale con il grafico corrispondente al poligono cliccato all'interno del dataset sulla mappa
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
      if (this.highlightedPolygon) {
        if (this.highlightedPolygon.pol.getBounds().contains(e.latlng)) {
          // console.log("POLYGON HIGHLIGHTED =", this.highlightedPolygon);
          this.openGraphDialog(null, null, this.highlightedPolygon)
        }
      }

      // const polygonsContainingPoint = this.allPolygons.filter((polygon: any) => {
      //   const copiaPoly = _.cloneDeep(polygon);
      //   // console.log("Polygon copy: ", copiaPoly);
      //   if (this.isPointInsidePolygon(e.latlng, polygon.pol)) {
      //     console.log("POLYGON =", polygon);

      //     return polygon;
      //   }
      //   // if (polygon.pol.getBounds().contains(e.latlng)) {
      //   //   return polygon;
      //   // }

      //   // return polygon.pol.getBounds().contains(e.latlng);
      // }); //poligono che contiene il punto in cui l'utente ha cliccato

      // if (polygonsContainingPoint.length > 0) {

      //   this.openGraphDialog(null, null, polygonsContainingPoint)

      // }
      else {
        this.alertSelectPolygon = {
          openAlert: true,
          text: "Select a polygon"
        };
        // alert("Select a polygon");
      }
    }
  }

  /**
   * Metodo richiamato al click sulla mappa
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

  /**
   * Funzione che viene richiamata quando si clicca sul marker
   */
  markerPointClick() {
    this.openGraphDialog();

  }

  removeMarker() {
    // this.map.removeLayer(this.markerPoint);
  }

  /**
   * Funzione che viene chiamata al click del marker
   */
  onMarkerClick(event: any) {
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
   * Funzione che rihciama tutti i nuovi dataset di erddap attraverso i servizi api collegati ai nodi del database
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
        // console.log("RES NODES =", res.nodes);

        this.resAllNodes = res.nodes;

        this.resAllNodes.forEach((element: any) => {
          // if(element.adriaclim_dataset !== "no" && element.adriaclim_dataset !== "No" && element.adriaclim_dataset !== "Indicator") {
          //   tmpCategoryDatasets.push(element.adriaclim_dataset);
          // }
          // if(element.adriaclim_dataset === this.formMenuDatasets.get("category")?.value) {
          //   tmpScale.push(element.adriaclim_scale);
          // }
          // if(element.adriaclim_dataset === this.formMenuDatasets.get("category")?.value && element.adriaclim_scale === this.formMenuDatasets.get("scale")?.value) {
          //   tmpTimeperiods.push(element.adriaclim_timeperiod);
          // }
          this.dataAllNodes.push(
            { name: element }
          );
        });

        // this.categoryDatasets = [...new Set(tmpCategoryDatasets)];
        // this.formMenuDatasets.get("category")?.setValue(this.categoryDatasets[0]);
        // this.scaleDatasets = [...new Set(tmpScale)];
        // this.formMenuDatasets.get("scale")?.setValue(this.scaleDatasets[0]);
        // this.timeperiodDatasets = [...new Set(tmpTimeperiods)];
        // this.formMenuDatasets.get("timeperiod")?.setValue(this.timeperiodDatasets[0]);

        // this.menuDatasets = this.resAllNodes.filter((el: any) => el.adriaclim_dataset === this.formMenuDatasets.get("category")?.value && el.adriaclim_scale === this.formMenuDatasets.get("scale")?.value && el.adriaclim_timeperiod === this.formMenuDatasets.get("timeperiod")?.value);

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
        console.log("SUB ERROR");

        console.log('ALL NODES ERROR: ', msg);
      }
    })
    // this.dataSource.data = TREE_DATA;

  }

  /**
   * Funzione che ritorna tutti i dati per popolare poi il tree
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
   * Funzione che popola la lista dei layer attivi nel pannello active layers
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
   * Funzione che viene lanciata ogni volta che si cambia la selezione del layer attraverso la lista degli active layers per aggiornare la mappa
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
   * Funzione che permette di recuperare i metadata dei dataset
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
   * Funzione che prende in input il nodo e gestisce le sue informazioni per esempio le variabili
   */
  getSelectedNode(node: any) {
    this.variableArray = [];

    if (node.name) {
      let variableNames = node.name.variable_names.split(" ");
      let variableTypes = node.name.variable_types.split(" ");
      variableNames.forEach((variableName: any, index: number) => {
        // Include variables that are not "time", "latitude", or "longitude" and have a type of "float"

        if (
          variableName !== "time" && variableName !== "latitude" && variableName !== "longitude" &&
          (variableTypes[index] !== "float" || variableTypes[index] !== "double")
        ) {

          this.variableArray.push({ name: variableName, type: variableTypes[index] });
        }
      });
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
      // this.variableArray = node.variable_names.split(" ");
    }
    // this.isIndicator = node.name.griddap_url !== "" ? false : true; //true se è tabledap, false se è griddap
    // if (this.isIndicator) {

    //   this.variableArray = this.variableArray.slice(-1);
    // }

    if (this.variableArray.length > 0) {
      this.variableGroup.get("variableControl")?.setValue(this.variableArray[this.variableArray.length - 1]["name"]);

    }

  }

  /**
   * Funzione che permette di recuperare l'ultimo giorno del mese
   */
  lastday(y: any, m: any) {

    return new Date(y, m + 1, 0).getDate();
  }

  /**
   * Funzione che ritorna il mese reale successivo
   */
  addRealMonth(d: any, months: any) {
    const fm = moment(d).add(months, 'M');
    const fmEnd = moment(fm).endOf('month');
    return d.date() != fm.date() && fm.isSame(fmEnd.format('YYYY-MM-DD')) ? fm.add(1, 'd') : fm;
  }

  /**
   * Funzione che ritorna il mese reale precedente
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
    // d.setDate(d.getDate() + 1);
    if (d.getDate() === 1) {
      return true;
    } else {
      return false;
    }
  }

  /**
   * Funzione che restituisce true o false se il valore passato è di tipo stringa o no
   */
  isAString(val: any): boolean { return typeof val === 'string'; }

  disableArrowDate() {
    let selD = _.cloneDeep(this.selectedDate.get("dateSel")?.value);

    // if(this.selectedDate.get("dateSel")?.value.toString() === this.dateStart.toString()) {
    if (selD.getFullYear() === this.dateStart.getFullYear() && selD.getMonth() === this.dateStart.getMonth() && selD.getDate() === this.dateStart.getDate()) {

      this.navigateDateLeftMonth = true;
      this.navigateDateRightMonth = false;
      this.navigateDateRightSeason = false;
      this.navigateDateRightYear = false;
      this.navigateDateLeftYear = false;
      this.navigateDateLeftSeason = false;
    }
    else if (selD.getFullYear() === this.dateEnd.getFullYear() && selD.getMonth() === this.dateEnd.getMonth() && selD.getDate() === this.dateEnd.getDate()) {

      this.navigateDateLeftMonth = false;
      this.navigateDateRightMonth = true;
      this.navigateDateRightSeason = false;
      this.navigateDateRightYear = false;
      this.navigateDateLeftYear = false;
      this.navigateDateLeftSeason = false;
    }
    else {

      this.navigateDateLeftMonth = false;
      this.navigateDateRightMonth = false;
      this.navigateDateRightSeason = false;
      this.navigateDateRightYear = false;
      this.navigateDateLeftYear = false;
      this.navigateDateLeftSeason = false;
    }

  }

  /**
   * Funzione che permette di gestire ogni casistica legata ai bottoni per il cambio data
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
     * Get layer 3D
     */
    /**
     * Slider
     */
    if (this.selData.get("dataSetSel")?.value.name.adriaclim_timeperiod === "yearly") {
      if (arrow === "left") {

        const selD = _.cloneDeep(this.selectedDate.get("dateSel")?.value);
        if ((selD.getFullYear() - 1) === this.dateStart.getFullYear()) {
          //it is the first year visible so after setting the new value we disable the left button
          selD.setFullYear(selD.getFullYear() - 1);
          selD.setMonth(this.dateStart.getMonth());
          selD.setDate(this.dateStart.getDate());
          this.selectedDate.get("dateSel")?.setValue(selD);
          this.navigateDateLeftYear = true;
          this.navigateDateRightYear = false;
          this.navigateDateRightMonth = false;
          this.navigateDateRightSeason = false;
          this.getMeta(metaId, "ok", this.valueCustom);
        } else {
          selD.setFullYear(selD.getFullYear() - 1);
          selD.setMonth(this.dateEnd.getMonth());
          selD.setDate(this.dateEnd.getDate());
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
          selD.setMonth(this.dateEnd.getMonth());
          selD.setDate(this.dateEnd.getDate());
          this.selectedDate.get("dateSel")?.setValue(selD);
          this.navigateDateRightYear = true;
          this.navigateDateLeftYear = false;
          this.getMeta(metaId, "ok", this.valueCustom);
        } else {
          selD.setFullYear(selD.getFullYear() + 1);
          selD.setMonth(this.dateEnd.getMonth());
          selD.setDate(this.dateEnd.getDate());
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
    else {
      // CASO DAILY
      if (arrow === "left") {
        let selD = _.cloneDeep(this.selectedDate.get("dateSel")?.value);
        const d1 = _.cloneDeep(selD);
        let d2 = _.cloneDeep(selD);

        // Tolgo un giorno a d2
        d2.setDate(d2.getDate() - 1);

        // Verifico se d2 è il primo giorno del mese o il primo giorno dell'anno
        if (d2.getDate() === 1) {


          if (d2.getMonth() === 0) {

            // Se è il primo giorno di gennaio, vai all'ultimo giorno di dicembre dell'anno precedente
            d2.setFullYear(d2.getFullYear() - 1);
            d2.setMonth(11); // Dicembre
            d2.setDate(31); // Ultimo giorno di dicembre
          }
          else if (d1.getDate() === 2 && d2.getDate() === 1) {

            // Se la data selezionata era il secondo giorno del mese,
            // e ora d2 è diventato il primo giorno, vai al primo giorno del mese
            d2.setDate(1);
          }
          else {

            // Altrimenti, vai all'ultimo giorno del mese precedente
            d2.setDate(0); // Ultimo giorno del mese precedente
            console.log("D2 = ", d2);
            console.log("D2 = ", d2.getDate(0));

          }
        }

        // Imposta l'orario su quello specifico se necessario
        d2.setHours(this.dateStart.getHours(), this.dateStart.getMinutes(), this.dateStart.getSeconds());

        // Verifica se d2 è minore o uguale a this.dateStart
        if (d2 <= this.dateStart) {
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
      else if (arrow === "right") {

        let selD = _.cloneDeep(this.selectedDate.get("dateSel")?.value);
        const d1 = _.cloneDeep(selD);
        let d2 = _.cloneDeep(selD);

        // Aggiungo un giorno a d2
        d2.setDate(d2.getDate() + 1);

        // Verifico se d2 è il primo giorno del mese o il primo giorno dell'anno
        if (this.isLastDayOfMonth(d2)) {

          if (d2.getMonth() === 11) {

            // Se è il primo giorno di gennaio, vai all'ultimo giorno di dicembre dell'anno precedente
            d2.setFullYear(d2.getFullYear() + 1);
            d2.setMonth(); // Gennaio
            d2.setDate(1); // Primo giorno di dicembre
          }
          else if (this.isLastDayOfMonth(d1 - 1) && d2.getDate() === 1) {

            d2.setDate(d1);
          }
          else {

            // Altrimenti, vai al primo giorno del mese precedente
            d2.setMonth(d1.getMonth() + 1);
            d2.setDate(1); // Primo giorno del mese precedente
            console.log("D2 = ", d2);
            console.log("D2 = ", d2.getDate(0));

          }
        }

        d2.setHours(this.dateEnd.getHours(), this.dateEnd.getMinutes(), this.dateEnd.getSeconds());
        if (d2 >= this.dateEnd) {
          selD = d2;
          this.selectedDate.get("dateSel")?.setValue(selD);
          this.navigateDateLeftMonth = false;
          this.navigateDateRightMonth = true;
          this.navigateDateRightSeason = false;
          this.navigateDateRightYear = false;
          this.navigateDateLeftYear = false;
          this.navigateDateLeftSeason = false;
          this.getMeta(metaId, "ok", this.valueCustom);
        }
        else {
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
   * Funzione che gestisce il parametro aggiuntivo per il caso senza WMS mostrando, dove c'è il parametro, il nome e i valori corretti
   */
  extraParamNoWms(metadata: any, controlExtra?: any) {
    const num_parameters = metadata[0][1].split(", ");
    const min_max_value = metadata[0][0].split(",");
    const name = num_parameters[1];
    const min = Number(min_max_value[0]);
    const max = Number(min_max_value[1]);
    const step = Number(metadata[0][5].split("=")[1]);

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

    this.metadata = this.metadata["metadata"];

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
      this.spinnerLoader.spinnerShow = true;

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

        this.legendLayer_src = this.ERDDAP_URL + "/griddap/" + idMeta + ".png?" + layer_name + "%5B(" + this.formatDate(time) + ")%5D%5B%5D%5B%5D&.legend=Only";

      } else {

        const min_max_value = this.metadata[0][0].split(",");
        const name = num_parameters[1];
        const min = Number(min_max_value[0]);
        const max = Number(min_max_value[1]);
        const step = Number(this.metadata[0][5].split("=")[1]);

        if (name === "depth") {
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

      setTimeout(() => {
        this.spinnerLoader.spinnerShow = false;

      }, 500);

    }

  }

  sliderControl(event: any) {

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
   * Funzione che permette di formattare ottenendo la formattazione corretta da visualizzare
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
   * Tree
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
   * Funzione che apre la modale contenente la tabella dei metadati del dataset selezionato
   */
  openTableDialog(idMeta?: any, title?: any, n?: any) {
    let dataId: any;

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

    const dialogRef = this.dialog.open(GeoportalMapDialogComponent, dialogConfig);

  }

  /**
   * Funzione che permette di aprire la modale contenente il grafico del dataset selezionato
   */
  openGraphDialog(lat?: any, lng?: any, polygon?: any) {

    const dialogConfig = new MatDialogConfig();
    dialogConfig.disableClose = true;
    dialogConfig.autoFocus = true;

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
        // polyExport: polygon ? polygon[0].pol.getBounds() : null,
        // polygon: polygon ? polygon[0].pol.getLatLngs()[0] : null,
        // polName: polygon ? polygon[0].polName : null,
        polyExport: polygon ? polygon.pol.getBounds() : null,
        polygon: polygon ? polygon.pol.getLatLngs()[0] : null,
        polName: polygon ? polygon.polName : null,
        circleCoords: this.circleCoords,
        isIndicator: this.isIndicator ? "true" : "false",
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

    const dialogRef = this.dialog.open(GeoportalMapDialogComponent, dialogConfig);

  }

  /**
   * Funzione che permette di aprire una snackbar di angular material per mostrare una notifica
   */
  openSnackBar(message: string, action: string, horizontal: MatSnackBarHorizontalPosition, vertical: MatSnackBarVerticalPosition) {
    this._snackBar.open(message, action, {
      horizontalPosition: horizontal,
      verticalPosition: vertical,
    });
  }

  /**
   * Funzione che rimuove tutte le legende al momento applicate alla mappa
   */
  removeAllLegends() {
    this.allLegendsNoWms.forEach((legend: any) => {
      this.map.removeControl(legend);
    });
    this.allLegendsNoWms = [];
  }

  /**
   * Funzione che rimuove tutti i rettangoli al momento applicati alla mappa
   */
  removeAllRectangles() {
    this.allRectangles.forEach((rectangle: any) => {
      this.map.removeLayer(rectangle);
    });
    this.allRectangles = [];
  }

  /**
   * Prendiamo i dati del dataset tabledap selezionato
   */
  getDataVectorialTabledap() {

    this.rettangoliLayer.clearLayers();
    this.removeAllLegends();

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
    // Settiamo un timeout per permettere un multiclick sul bottone
    // setTimeout(() => {
    this.spinnerLoader.spinnerShow = true;
    // }, 500);

    this.httpService.post('test/dataVectorial', {
      dataset: this.selData.get("dataSetSel")?.value.name,
      // selVar: this.selData.get("dataSetSel")?.value.name.griddap_url !== "" ? this.variableGroup.get("variableControl")?.value : splittedVar,
      selVar: this.variableGroup.get("variableControl")?.value,
      isIndicator: this.isIndicator ? "true" : "false",
      selDate: this.formatDate(this.selectedDate.get("dateSel")?.value),
    }).subscribe({
      next: (res: any) => {
        if (res.dataVect.includes("HTTP Error 404")) {
          this.compliantErrorErddap = "The data is not compliant"

          // Alert tramite bootstrap con html
          this.showAlertGenericError = true;

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
          if (parseFloat(value_min) !== parseFloat(value_max)) {
            if (parseFloat(value_min) < 0) {
              value_mid = Math.ceil((parseFloat(value_max) - parseFloat(value_min)) / 2);
            } else {
              value_mid = Math.ceil((parseFloat(value_max) + parseFloat(value_min)) / 2);
            }
          }
          else {
            value_mid = parseFloat(value_min);
          }
          this.valueMin = parseFloat(value_min);
          this.valueMax = parseFloat(value_max);
          this.valueMid = value_mid;

          this.createLegend(parseFloat(value_min), parseFloat(value_max), value_mid);
          if (this.allRectangles.length > 0) {
            this.removeAllRectangles();

          }
          // this.markersLayer = L.layerGroup();
          // markersLayer: L.LayerGroup = L.layerGroup();
          let centerLat;
          let centerLong;

          if (allLatCoordinates.length === 1) {
            centerLat = allLatCoordinates[0];
            centerLong = allLongCoordinates[0];

          } else {
            const center = Math.round(allLatCoordinates.length / 2);
            centerLat = allLatCoordinates[center];
            centerLong = allLongCoordinates[center];
          }

          const zoomTest = L.latLng(centerLat, centerLong);
          if (zoomTest) {
            if (allLatCoordinates.length === 1) {
              // zoom più elevato essendo un singolo punto!
              this.map.setView(zoomTest, 14);
            } else {
              this.map.setView(zoomTest, 8);
            }

          }

          for (let i = 0; i < allLatCoordinates.length; i++) {

            if (this.isIndicator) {

              if (!isNaN(parseFloat(allLatCoordinates[i])) || !isNaN(parseFloat(allLongCoordinates[i]))) {

                this.circleCoords.push(
                  {
                    lat: allLatCoordinates[i],
                    lng: allLongCoordinates[i],
                  }
                )
                //tabledap case, with circle
                const colorStorage = localStorage.getItem(this.selData.get("dataSetSel")?.value.name.title);

                let varColor: any;
                if (colorStorage) {

                  const colorStorageJson = JSON.parse(colorStorage);
                  varColor = this.getColor(allValues[i], value_min, value_max, colorStorageJson.minColor, colorStorageJson.midColor, colorStorageJson.maxColor);
                } else {

                  varColor = this.getColor(allValues[i], value_min, value_max, "#f44336", "#9c27b0", "#3f51b5");
                }

                this.map.removeLayer(this.rettangoliLayer);

                this.markerToAdd = L.circleMarker([parseFloat(allLatCoordinates[i]), parseFloat(allLongCoordinates[i])], { radius: 15, weight: 2, color: this.fillRectangleColor(varColor.r, varColor.g, varColor.b) });
                this.circleMarkerArray.push(this.markerToAdd);
                this.markersLayer.addLayer(this.markerToAdd);

                this.map.addLayer(this.markersLayer);
              }

            } else {

              //griddap case with rectangle, NON SERVONO I MARKER!

              if (!isNaN(parseFloat(allLatCoordinates[i])) || !isNaN(parseFloat(allLongCoordinates[i]))) {

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

                rectangle = L.rectangle(bounds, { fillOpacity: 0.8, opacity: 0.8, fill: true, stroke: false, color: this.fillRectangleColor(varColor.r, varColor.g, varColor.b), weight: 1 });
                this.allRectangles.push(rectangle);

                this.rettangoliLayer.addLayer(rectangle);

                this.map.addLayer(this.rettangoliLayer);

              }

            }
          }
          if (this.circleMarkerArray.length > 0 && this.clickPointOnOff) {
            this.circleMarkerArray.forEach((circle: any) => {
              circle.addEventListener('click', (e: any) => this.openGraphDialog(circle.getLatLng().lat, circle.getLatLng().lng));
            });
            this.map.off('click');
          }
        }
        setTimeout(() => {
          this.spinnerLoader.spinnerShow = false;

        }, 500);

      },
      error: (msg: any) => {
        console.log('METADATA ERROR: ', msg);
        this.spinnerLoader.spinnerShow = false;
      }

    });
  }

  /**
   * Prendiamo i dati del dataset tabledap selezionato (vecchia)
   */
  getDataVectorialTabledapOld() {

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

    // this.spinnerLoader.spinnerShow = true;

    this.httpService.post('test/dataVectorial', {
      dataset: this.selData.get("dataSetSel")?.value.name,
      // selVar: this.selData.get("dataSetSel")?.value.name.griddap_url !== "" ? this.variableGroup.get("variableControl")?.value : splittedVar,
      selVar: this.variableGroup.get("variableControl")?.value,
      isIndicator: this.isIndicator ? "true" : "false",
      selDate: this.formatDate(this.selectedDate.get("dateSel")?.value),
    }).subscribe({
      next: (res: any) => {
        // console.log("RES =", res);
        if (res.dataVect.includes("HTTP Error 404")) {
          this.compliantErrorErddap = "The data is not compliant"
          // console.log("ERR =", this.compliantErrorErddap);

          // Alert tramite bootstrap con html
          this.showAlertGenericError = true;

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
            centerLat = allLatCoordinates[center];
            centerLong = allLongCoordinates[center];
          }

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

        // setTimeout(() => {
        //   this.spinnerLoader.spinnerShow = false;

        // }, 500);

      },
      error: (msg: any) => {
        console.log('METADATA ERROR: ', msg);
        this.spinnerLoader.spinnerShow = false;
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

      let rValue = Math.floor((1 - f) * l.r + f * r.r);
      let gValue = Math.floor((1 - f) * l.g + f * r.g);
      let bValue = Math.floor((1 - f) * l.b + f * r.b);

      return {
        r: rValue,
        g: gValue,
        b: bValue,
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
    }
    else {
      left = { r: this.hexToRgb(colorMin)?.r, g: this.hexToRgb(colorMin)?.g, b: this.hexToRgb(colorMin)?.b },
        middle = { r: this.hexToRgb(colorMid)?.r, g: this.hexToRgb(colorMid)?.g, b: this.hexToRgb(colorMid)?.b },
        right = { r: this.hexToRgb(colorMax)?.r, g: this.hexToRgb(colorMax)?.g, b: this.hexToRgb(colorMax)?.b },
        mid = (max - min) / 2;

    }
    if (min === max) {
      mid = min;
      this.sameColor = true;
    }
    else {
      this.sameColor = false;
    }

    return v < min + mid ?
      getC((v - min) / mid, left, middle) :
      getC((v - min - mid) / mid, middle, right);
  }

  /**
   * Funzione che permette di ripristinare i colori di default della legenda
   */
  restoreDefaultColors() {
    this.valueMinColor = this.valueMinColorDefault;
    this.valueMidColor = this.valueMidColorDefault;
    this.valueMaxColor = this.valueMaxColorDefault;
    this.valueMinMidColor = this.valueMinMidColorDefault;
    this.valueMidMaxColor = this.valueMidMaxColorDefault;

  }

  /**
   * Funzione che permette di creare la legenda per i dati senza WMS
   */
  createLegend(value_min: any, value_max: any, value_mid: any) {
    this.removeAllLegends();

    let value_min_mid: any;
    let value_mid_max: any;
    this.legendNoWms = new L.Control({ position: "bottomleft" });
    if (parseFloat(value_min) !== parseFloat(value_max)) {
      if (parseFloat(value_min) < 0) {

        value_min_mid = Math.ceil((parseFloat(value_mid) - parseFloat(value_min)) / 2);
        value_mid_max = Math.ceil((parseFloat(value_max) - parseFloat(value_mid)) / 2);
      }
      else {
        value_min_mid = Math.ceil((parseFloat(value_mid) + parseFloat(value_min)) / 2);
        value_mid_max = Math.ceil((parseFloat(value_max) + parseFloat(value_mid)) / 2);
      }

    }
    else {
      value_min_mid = parseFloat(value_min);
      value_mid_max = parseFloat(value_max);
    }

    value_min = this.formatNumber(value_min, 5);
    value_min_mid = this.formatNumber(value_min_mid, 5);
    value_mid = this.formatNumber(value_mid, 5);
    value_mid_max = this.formatNumber(value_mid_max, 5);
    value_max = this.formatNumber(value_max, 5);

    const getColor = (v: any) => {
      const colorStorage = localStorage.getItem(this.selData.get("dataSetSel")?.value.name.title);
      let colorStorageObj: any;
      if (colorStorage) {
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

        if (from !== to) {
          labels.push(
            "<div class='color-number-legend'>" + '<i style="background:' + getColor(from) + '; margin-right: 10px;"></i> ' +
            "<span>" + from + (to ? '&ndash;' + to : "") + "</span>" + "</div>"
          );
        }
      }

      if (from === to) {
        labels.push(
          "<div class='color-number-legend'>" + '<i style="background:' + getColor(from) + '; margin-right: 10px;"></i> ' +
          "<span>" + from + "</span>" + "</div>"
        );
      }

      const button = L.DomUtil.create('button', 'color-number-legend');
      button.innerHTML = `<span class='material-symbols-outlined'>settings</span>`;
      button.addEventListener('click', (e) => this.changeLegendColors());

      div.innerHTML = labels.join('');
      div.appendChild(button);
      return div;
    };
    // ********** LEGENDA NO WMS **********
    this.legendNoWms.addTo(this.map);

    this.allLegendsNoWms.push(this.legendNoWms);

  }

  /**
   * Funzione che permette di creare la legenda per i dati senza WMS (vecchia)
   */
  createLegendOld(value_min: any, value_max: any, value_mid: any) {
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

    value_min = this.formatNumber(value_min, 5);
    value_min_mid = this.formatNumber(value_min_mid, 5);
    value_mid = this.formatNumber(value_mid, 5);
    value_mid_max = this.formatNumber(value_mid_max, 5);
    value_max = this.formatNumber(value_max, 5);

    const getColor = (v: any) => {
      const colorStorage = localStorage.getItem(this.selData.get("dataSetSel")?.value.name.title);
      let colorStorageObj: any;
      if (colorStorage) {
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
   * Funzione che permette di aprire la modale per il confronto tra due dataset
   */
  compareDialogModal = () => {
    this.clickPointOnOff = true;
    const dialogConfig = new MatDialogConfig();

    dialogConfig.disableClose = true;
    dialogConfig.autoFocus = true;

    dialogConfig.data = {
      activeLayersArray: this.activeLayersArray,
    };

    const dialogRef = this.dialog.open(GeoportalCompareDialogComponent, dialogConfig);
    //prendere i due layers selezionati!
    dialogRef.afterClosed().subscribe(async result => {
      if (result != "") {
        // this.allPolygons.forEach(element => {
        //   element.pol.off("mouseover");
        // });
        // console.log("result =", result);
        this.datasetCompare = result;
        this.confronto = true;
        this.compare = true;
        this.pointSelect();

      }
    })

  }

  /**
   * Funzione che permette di cambiare i colori della legenda
   */
  changeLegendColors = (title?: string) => {

    this.rettangoliLayer.clearLayers();
    this.removeAllLegends();

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
      sameColor: this.sameColor,
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
   * Filtro per tree con lista al posto del tree
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

      }
    }
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
   * Funzione che controlla quale bottone è stato cliccato aprendo e chiudendo il menu corrispondente
   */
  checkExpand(collapse: string) {
    if (collapse === "first") {
      this.isExpandedFirst = !this.isExpandedFirst;
      if (this.isExpandedFirst) {
        this.isExpandedSecond = false;
        this.isExpandedThird = false;
        this.isExpandedFourth = false;
      }
    }
    else if (collapse === "second") {
      this.isExpandedSecond = !this.isExpandedSecond;
      if (this.isExpandedSecond) {
        this.isExpandedFirst = false;
        this.isExpandedThird = false;
        this.isExpandedFourth = false;
      }
    }
    else if (collapse === "third") {
      this.isExpandedThird = !this.isExpandedThird;
      if (this.isExpandedThird) {
        this.isExpandedFirst = false;
        this.isExpandedSecond = false;
        this.isExpandedFourth = false;
      }
    }
    else if (collapse === "fourth") {
      this.isExpandedFourth = !this.isExpandedFourth;
      if (this.isExpandedFourth) {
        this.isExpandedFirst = false;
        this.isExpandedSecond = false;
        this.isExpandedThird = false;
      }
    }
  }

  /**
   * Funzione che cambia dinamicamente gli elementi all'interno dei vari menu
   */
  changeSel(sel?: any, type?: string) {

    let tmpScale: any[] = [];
    let tmpTimeperiods: any[] = [];

    if (type === "c") {

      this.resAllNodes.forEach((el: any) => {
        if (el.adriaclim_dataset === this.formMenuDatasets.get("category")?.value) {
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
    else if (type === "s") {
      this.resAllNodes.forEach((el: any) => {
        if (el.adriaclim_dataset === this.formMenuDatasets.get("category")?.value && el.adriaclim_scale === this.formMenuDatasets.get("scale")?.value) {
          tmpTimeperiods.push(el.adriaclim_timeperiod);
        }
      });
      this.timeperiodDatasets = [...new Set(tmpTimeperiods)];
      this.formMenuDatasets.get("timeperiod")?.setValue(this.timeperiodDatasets[0]);

    }
    else if (type === "t") {
      this.menuDatasets = this.resAllNodes.filter((el: any) => el.adriaclim_dataset === this.formMenuDatasets.get("category")?.value && el.adriaclim_scale === this.formMenuDatasets.get("scale")?.value && el.adriaclim_timeperiod === this.formMenuDatasets.get("timeperiod")?.value);
    }

  }

  /**
   * Funzione che carica il layer corrispondente sulla mappa alla selezione di un dataset
   */
  selDatasetFromDialog(node: any) {
    let obj = {
      name: node
    }

    this.getMeta(obj.name.id);
    this.addToActiveLayers(obj);
    this.getSelectedNode(obj);

  }

  /**
   * Funzione che permette di aprire la modale con la scelta dei dataset
   */
  openDatasetMenu() {
    const dialogConfig = new MatDialogConfig();

    dialogConfig.disableClose = true;
    dialogConfig.autoFocus = true;
    //dobbiamo passargli la lista dei layers attivi!

    dialogConfig.data = {
      categoryDatasets: this.categoryDatasets,
      scaleDatasets: this.scaleDatasets,
      timeperiodDatasets: this.timeperiodDatasets,
      menuDatasets: this.menuDatasets,
      resultMenuDialog: this.resultMenuDialog,
    };
    dialogConfig.position = { top: '4%' };

    const dialogRef = this.dialog.open(GeoportalMapMenuDialogComponent, dialogConfig);
    //prendere i due layers selezionati!
    dialogRef.afterClosed().subscribe(async result => {
      if (result != "") {
        this.selDatasetFromDialog(result.menu);

        this.resultMenuDialog = result;
      }
    })

  }

}
