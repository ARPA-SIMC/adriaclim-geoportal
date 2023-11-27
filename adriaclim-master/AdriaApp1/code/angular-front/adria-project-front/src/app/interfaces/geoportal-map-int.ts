export interface FoodNode {
  name: string;
  value?: string;
  childVisible?: boolean;
  children?: FoodNode[];
}

export interface ExtendedWMSOptions extends L.TileLayerOptions {
  bgcolor?: string;
  time?: string;
}

export interface LatLng {
  lat: number;
  lng: number;
}

export interface ExtraParams {
  name: string;
  nameExtraParam: string;
  minValue: number;
  maxValue: number;
  stepSize: number;
}

export interface circleCoords {
  lat: any;
  lng: any;
}

export interface ExampleFlatNode {
  expandable: boolean;
  name: string;
  level: number;
}
