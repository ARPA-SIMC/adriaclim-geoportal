import { FlatTreeControl, NestedTreeControl } from '@angular/cdk/tree';
import { HttpClient } from '@angular/common/http';
import { AfterViewInit, Component, ElementRef, OnInit, ViewChild } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import { MatMenuTrigger } from '@angular/material/menu';
import { MatTreeFlatDataSource, MatTreeFlattener, MatTreeNestedDataSource } from '@angular/material/tree';
import * as L from 'leaflet';
import { latLng, marker, Marker, icon } from 'leaflet';
import { map } from 'rxjs';
import * as poly from '../../assets/geojson/gj.json';


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

  selData: FormGroup;

  metadata: any;

  constructor(private httpClient: HttpClient) {
    this.selData = new FormGroup({
      dataSetSel: new FormControl()
    });

    this.getInd();
    // this.dataSource.data = TREE_DATA;

  }
  async ngAfterViewInit(): Promise<void> {

    await this.initMap();
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

    // await this.initMap();

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

  addPolygons() {

  }

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
    console.log("MENU TRIGGER =", menuTrigger);

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
        console.log('PLUTO: ', position);
      },
      error(msg) {
        console.log('PLUTO ERROR: ', msg);
      }
    });
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
        console.log('IND: ', res);

        this.dataInd = res.ind;

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
          
          console.log("TREE DATA =", TREE_DATA);
          this.dataSource.data = TREE_DATA;
      },
      error: (msg: any) => {
        console.log('IND ERROR: ', msg);
      }

    });

  }

  getMeta(idMeta: any) {
    this.httpClient.post('http://localhost:8000/test/metadata', {
      idMeta: idMeta
    }).subscribe({
      next: (res: any) => {
        console.log('METADATA: ', res);
        this.metadata = res;
        this.getLayers(idMeta);
      },
      error: (msg: any) => {
        console.log('METADATA ERROR: ', msg);
      }

    });

  }

  getLayers(idMeta: any) {
    // attribution: metadata[6],
    // bgcolor: '0x808080',
    // crs: L.CRS.EPSG4326,
    // format: 'image/png',
    // layers: dataset_id+':'+layer_name,
    // styles: '',
    // time: timeValue,
    // transparent: true,
    // version: '1.3.0',
    // opacity:0.7,

    let d = new Date()
    // d.setUTCSeconds
    this.metadata = this.metadata["metadata"];

    console.log("METADATAaaaa ==", this.metadata);
    // d.setUTCSeconds
    console.log("METADATA 2 ==", this.metadata[0][2]);

    let seconds_epoch = this.metadata[0][2].split(",");

    let seconds_epoch_start = seconds_epoch[0];

    let seconds_epoch_end = seconds_epoch[1];

    let date_start=new Date(0);
    date_start.setUTCSeconds(seconds_epoch_start);
    let date_end=new Date(0);
    date_end.setUTCSeconds(seconds_epoch_end.trim());

    let time = this.formatDate(date_start);

    console.log("TIME======== ",time);

    //NOT WORKING!!
    let layer_to_attach={
      layer_name: L.tileLayer.wms( 
      'http://localhost:8000/test/layers2d',{
      attribution: this.metadata[0][6],
      bgcolor: '0x808080',
      crs: L.CRS.EPSG4326,
      format: 'image/png',
      layers: idMeta +':'+this.metadata[0][4],
      styles: '',
      time: time,
      transparent: true,
      version: '1.3.0',
      opacity:0.7,
      } as ExtendedWMSOptions
      )
  };

  layer_to_attach.layer_name.addTo(this.map);

    

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

}



