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

interface LatLng {
  lat: number;
  lng: number;
}

interface ExtraParams {
  name: string;
  nameExtraParam: string;
  minValue: number;
  maxValue: number;
  stepSize: number;
}

interface circleCoords {
  lat: any;
  lng: any;
}

interface ExampleFlatNode {
  expandable: boolean;
  name: string;
  level: number;
}
