import { DatePipe } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Component, ElementRef, Inject, ViewChild, ChangeDetectorRef, AfterContentChecked } from '@angular/core';
import { FormBuilder, FormControl, FormGroup, Validators } from '@angular/forms';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { MatPaginator } from '@angular/material/paginator';
import { MatTableDataSource } from '@angular/material/table';
import { Options, LabelType } from '@angular-slider/ngx-slider';
import { HttpService } from 'src/app/services/http.service';
import { MAT_SELECT_CONFIG } from '@angular/material/select';
import * as _ from 'lodash';
import { OptionsValue, TypeOfExport } from 'src/app/interfaces/geoportal-map-dialog-int';
import { SpinnerLoaderService } from 'src/app/services/spinner-loader.service';

@Component({
  selector: 'app-geoportal-map-dialog',
  templateUrl: './geoportal-map-dialog.component.html',
  styleUrls: ['./geoportal-map-dialog.component.scss'],
  providers: [
    {
      provide: MAT_SELECT_CONFIG,
      useValue: { overlayPanelClass: 'select-overlay-pane-dialog' }
    }
  ]
})
export class GeoportalMapDialogComponent implements AfterContentChecked {

  showTutorialGraph = false;
  isUpdate = false;
  dimUnit: any;
  availableDepths: number[] = [];
  selectedDepth = 0;
  isProfileTimeseries = false;
  stats: any = {};
  displayedColumns: string[] = [];
  dataSource: MatTableDataSource<any> = new MatTableDataSource();
  metadataRows: any[] = [];
  spinnerLoading: any = false;
  progressBarAtStart = true;
  private paginator!: MatPaginator;
  dataTable: any;
  form!: FormGroup;
  description: string;
  tableDescription = "";
  success: boolean;
  datasetId: string;
  datasetName: string;
  openGraph: any;
  dataset: any;
  latlng: any;
  dateStart: any;
  dateEnd: any;
  stepDate: any;
  stepMilliseconds: any;
  variable: any;
  confronto: any;
  range: any;
  arrayVariable: any;
  extraParamExport: any;
  dataOutputGraph: any[] = [];
  stepDateExport: any;
  stepSizeExport: any;
  dataMinExport: any;
  dataMaxExport: any;
  minValue: any;
  maxValue: any;
  meanValue: any;
  medianValue: any;
  stdevValue: any;
  trendValue: any;
  statCalc: any;
  tutorialMode = false;
  prodDev = this.httpService.apiUrl === "http://localhost:8000/" ? "dev" : "prod";
  info: any = false;
  circleCoords: any;
  operation: any = "default";
  statistic: any = "avg";
  isIndicator: any;
  polygon: any;
  polyExport: any;
  polName: any;
  minRange: any;
  maxRange: any;
  options: Options = {
    floor: 0,
    ceil: 100,
  };

  optionsExtra: Options = {
    floor: 0,
    ceil: 100,
  };

  start: any;
  end: any;

  showStatistic = true;
  graphTutorialDriver: any;
  compareObj: any;

  progress = 0
  progressWidth = this.progress + "%"
  fakeProgressInterval: any;  
  private fakeProgressStepInterval: any = null;
  isFakeActive = false;
  fakeProgressStartedAt = 0;
  readonly MIN_VISIBLE_MS = 600; 
  

  typeOfExport: TypeOfExport[] = [
    {
      type: ".csv",
      label: ".csv - Download a ISO-8859-1 comma-separated text table (line 1: names; line 2: units; ISO 8601 times).",
    },
    {
      type: ".json",
      label: ".json - View a table-like UTF-8 JSON file (missing value = 'null'; times are ISO 8601 strings).",
    },
    {
      type: ".largePdf",
      label: ".largePdf - View a large .pdf image file with a graph or map.",
    },
    {
      type: ".largePng",
      label: ".largePng - View a large .png image file with a graph or map.",
    },
    {
      type: ".mat",
      label: ".mat - Download a MATLAB binary file.",
    },
    {
      type: ".nccsv",
      label: ".nccsv - Download a NetCDF-3-like 7-bit ASCII NCCSV .csv file with COARDS/CF/ACDD metadata."
    },
    {
      type: ".pdf",
      label: ".pdf - View a standard, medium-sized .pdf image file with a graph or map.",
    },
    {
      type: ".png",
      label: ".png - View a standard, medium-sized .png image file with a graph or map.",
    },
    {
      type: ".smallPdf",
      label: ".smallPdf - View a small .pdf image file with a graph or map.",
    },
    {
      type: ".transparentPng",
      label: ".transparentPng - View a .png image file (just the data, without axes, landmask, or legend).",
    },
  ]

  optionTimeScale: OptionsValue[] = [
    {
      label: "Default Graph",
      value: "default"
    },
    {
      label: "Annual Month by Month",
      value: "annualMonth"
    },
    {
      label: "Annual Season by Season",
      value: "annualSeason"
    },
    {
      label: "Annual Day by Day",
      value: "annualDay"
    },

  ]

  optionStatistics: OptionsValue[] = [
    {
      label: "Maximum Value (Moment By Moment)",
      value: "max"
    },
    {
      label: "Minimum Value (Moment By Moment)",
      value: "min"
    },
    {
      label: "Mean Value (Moment By Moment)",
      value: "avg"
    },
    {
      label: "10th Percentile",
      value: "10thPerc"
    },
    {
      label: "90th Percentile",
      value: "90thPerc"
    },
    {
      label: "Median",
      value: "median"
    },
    {
      label: "Space sum",
      value: "sum"
    },
    {
      label: "Min, Mean, Max",
      value: "min_mean_max"
    },
    {
      label: "Min, 10th Percentile, Median, 90th Percentile, Max",
      value: "min_10thPerc_median_90thPerc_max"
    },
    {
      label: "Box Plot",
      value: "boxPlot"
    }
  ];

  // startGraphTutorial(): void {

  //   this.graphTutorialDriver = driver({

  //     showProgress: true,
  //     animate: true,
  //     smoothScroll: true,
  //     allowClose: true,

  //     steps: [

  //       {
  //         element: '#tutorial-info-button',
  //         popover: {
  //           title: 'Dataset information',
  //           description: 'Open detailed information about the selected dataset, including metadata and technical details.',
  //           side: 'left',
  //           align: 'center'
  //         }
  //       },

  //       {
  //         element: '#tutorial-time-scale',
  //         popover: {
  //           title: 'Time scale',
  //           description: 'Change the temporal aggregation of the data, for example yearly, monthly or seasonal values.',
  //           side: 'right',
  //           align: 'center'
  //         }
  //       },

  //       {
  //         element: '#tutorial-statistics',
  //         popover: {
  //           title: 'Statistics',
  //           description: 'Select the statistical operation applied to the data, such as mean, median or trend calculation.',
  //           side: 'right',
  //           align: 'center'
  //         }
  //       },

  //       {
  //         element: '#tutorial-update-button',
  //         popover: {
  //           title: 'Update graph',
  //           description: 'After changing time scale or statistics, click Update to refresh the graph with the selected options.',
  //           side: 'bottom',
  //           align: 'center'
  //         }
  //       },

  //       {
  //         element: '#tutorial-chart',
  //         popover: {
  //           title: 'Zoom and chart tools',
  //           description: 'Use these tools to zoom into a specific time range, reset the zoom, restore the original chart view or save the graph as an image.',
  //           side: 'top',
  //           align: 'center'
  //         }
  //       }

  //     ]

  //   });

  //   // setTimeout(() => {
  //   //   this.graphTutorialDriver.drive();
  //   // }, 1000);

  // }
  showStat() {
    if (this.operation === "default") {

      this.showStatistic = true;
    }
    else {

      this.showStatistic = false;
    }
  }

  /**
  * Check whether to show statistics based on the operation selected above the modal chart
  */
  showStatPointSelected(checkPoly: any) {
    if (!checkPoly) {
      if (this.form.get('operationSel')?.value === "default") {

        this.showStatistic = true;
      }
      else {

        this.showStatistic = false;
      }

    }
  }

  /**
  * Show or hide the time scale dropdown menu
  */
  removeAnnualCycle(o: any): boolean {

    if (this.dataset.adriaclim_timeperiod === "yearly") {
      if (o.value === "annualMonth") {
        return true;
      }
      else if (o.value === "annualDay") {
        return true;
      }
      else if (o.value === "annualSeason") {
        return true;
      }
      else {
        return false;
      }
    }
    else if (this.dataset.adriaclim_timeperiod === "monthly" || this.dataset.adriaclim_timeperiod === "seasonal") {
      if (o.value === "annualDay") {
        return true;
      }
      else {
        return false;
      }
    }
    else {
      return false;
    }

  }

  /**
  * Enable or disable statistics within the statistics dropdown menu
  */
  disableStatistics(s: any): boolean {
    return false;
  }

  formatDate(d: any) {
    const month = d.getMonth() + 1
    const day = d.getDate()
    const year = d.getFullYear()
    return day + "/" + month + "/" + year;
  }

  formatDateExport(date: any) {
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


  // bypass ngIf for paginator
  @ViewChild(MatPaginator) set matPaginator(mp: MatPaginator) {

    this.paginator = mp;
    this.setDataSourceAttributes();

  }

  algoType: any;
  // @ViewChild('metadataTable') myDiv!: ElementRef;
  @ViewChild('graphDiv') graph!: ElementRef;

  constructor(
    private changeDetector: ChangeDetectorRef,
    private httpService: HttpService,
    public datePipe: DatePipe,
    private httpClient: HttpClient,
    private fb: FormBuilder,
    private dialogRef: MatDialogRef<GeoportalMapDialogComponent>,
    @Inject(MAT_DIALOG_DATA) data: any,
    public spinnerService: SpinnerLoaderService) {
    this.tutorialMode = data.tutorialMode || false;
    this.description = data.description;
    this.success = data.success;
    this.datasetId = data.datasetId;
    this.datasetName = data.datasetName;
    this.openGraph = data.openGraph;
    this.confronto = data.confronto;

    this.dataset = data.dataset;
    this.latlng = data.latlng;
    this.dateStart = data.dateStart;
    this.dateEnd = data.dateEnd;
    this.variable = data.variable;
    this.arrayVariable = data.arrayVariable;
    this.range = data.range;
    this.selectedDepth = data.range ? Number(data.range) : 0;
    this.isProfileTimeseries =
      !!this.dataset &&
      this.dataset.adriaclim_type === "timeseries" &&
      (this.dataset.dimension_names || "").toLowerCase().includes("depth") &&
      this.dataset.lat_min === this.dataset.lat_max &&
      this.dataset.lng_min === this.dataset.lng_max;
    this.extraParamExport = data.extraParamExport;
    this.isIndicator = data.isIndicator;
    this.polygon = data.polygon;
    this.polyExport = data.polyExport;
    this.polName = data.polName;
    this.circleCoords = data.circleCoords;
    this.compareObj = data.compareObj;
    if (this.dataset) {

      this.stepDate = this.dataset.adriaclim_timeperiod;
      if (this.tutorialMode) {
        this.stepDate = 'yearly';
        this.operation = 'default';
        this.statistic = 'avg';
        this.form.patchValue({
          operationSel: 'default',
          statisticSel: 'avg'
        });
        setTimeout(() => {
          // this.startGraphTutorial();
        }, 800);
      }
    }

    this.form = this.fb.group({
      cod: new FormControl(null),
      operationSel: new FormControl("default"),
      statisticSel: new FormControl("avg"),
      typeSel: new FormControl(this.typeOfExport[0].type),
      varSelected: new FormControl(null, Validators.required),
      enableArea: new FormControl(false),

      meanValue: new FormControl(null),
      medianValue: new FormControl(null),
      stdevValue: new FormControl(null),
      trendValue: new FormControl(null),

      prova: new FormControl(null),
    })
    if (this.dataset) {
      if (this.dataset.dimensions > 3 && this.dataset.wms_url !== "") {
        this.minRange = this.extraParamExport.minValue.toFixed(4);
        this.maxRange = this.extraParamExport.maxValue.toFixed(4);
        this.optionsExtra = {
          floor: this.extraParamExport.minValue,
          ceil: this.extraParamExport.maxValue,
          step: this.extraParamExport.stepSize.toFixed(4),
          draggableRange: true,
          noSwitching: true,
          translate: (value: number, label: LabelType): string => {
            if (value > 10000 || value < 0.001 && value !== 0) {
              return value.toExponential().replace(/e\+?/, ' x 10^');
            } else {
              return value.toString();
            }
          },
        };

      }

    }
  }

  /**
  * Change the chart modal content to display the section with chart-related information
  */
  showInfo() {
    const noInfo = document.getElementById("noInfo");
    const yesInfo = document.getElementById("yesInfo");
    if (noInfo && yesInfo) {
      if (noInfo.style.display == "none") {
        noInfo.style.display = "block";
        yesInfo.style.display = "none";
      }
      else {
        noInfo.style.display = "none";
        yesInfo.style.display = "flex";
      }
    }

  }

  ngAfterContentChecked(): void {
    this.changeDetector.detectChanges();
  }

  // bypass ngIf for paginator
  setDataSourceAttributes() {
    this.dataSource.paginator = this.paginator;

  }

  ngOnInit() {

    if (!this.openGraph) {
      this.getMetadataTable();
    }
    else {
      if (!this.polygon) {
        this.getGraphTable();
      }
    }
  }

  onDepthChange(value: any) {
    this.selectedDepth = Number(value);
    this.range = this.selectedDepth;

    // Show spinner immediately while the new depth is loading
    this.spinnerLoading = true;
    this.spinnerService.spinnerShow = true;

    this.isUpdate = true;
    setTimeout(() => {
      this.isUpdate = false;
    }, 0);
  }

  close() {
    this.dialogRef.close("");
  }

  formatMetadataLabel(label: string): string {
    if (!label) {
      return '';
    }

    return label
      .replace(/_/g, ' ')
      .replace(/\s+/g, ' ')
      .trim()
      .replace(/\b\w/g, (char) => char.toUpperCase());
  }

  buildMetadataRows(columnNames: string[], rows: any[][]): void {
    this.metadataRows = [];

    if (!columnNames || !rows || rows.length === 0) {
      return;
    }

    const findColumnIndex = (possibleNames: string[]): number => {
      return columnNames.findIndex((columnName: string) =>
        possibleNames.some((name) => columnName.trim().toLowerCase() === name.trim().toLowerCase())
      );
    };

    const rowTypeIndex = findColumnIndex(['Row Type', 'rowType', 'row_type']);
    const variableNameIndex = findColumnIndex(['Variable Name', 'variableName', 'variable_name']);
    const attributeNameIndex = findColumnIndex(['Attribute Name', 'attributeName', 'attribute_name']);
    const dataTypeIndex = findColumnIndex(['Data Type', 'dataType', 'data_type']);
    const valueIndex = findColumnIndex(['Value', 'value']);

    this.metadataRows = rows.map((row: any[]) => {
      return {
        rowType: rowTypeIndex >= 0 ? row[rowTypeIndex] : '',
        variableName: variableNameIndex >= 0 ? row[variableNameIndex] : '',
        attributeName: attributeNameIndex >= 0 ? this.formatMetadataLabel(row[attributeNameIndex]) : '',
        dataType: dataTypeIndex >= 0 ? row[dataTypeIndex] : '',
        value: valueIndex >= 0 ? row[valueIndex] : '',
      };
    });
  }

  /**
  * Retrieve metadata to populate the table
  */
  getMetadataTable() {
    const data = {
      idMeta: this.datasetId
    }
    this.spinnerService.spinnerShow = true;
    this.httpService.post('dataset/get_metadata_table/', data).subscribe((response: any) => {
      if (typeof response === 'string') {
        response = JSON.parse(response);
      }

      this.dataTable = response;

      const columnNames = this.dataTable.metadata.table.columnNames || [];
      const rows = this.dataTable.metadata.table.rows || [];

      this.buildMetadataRows(columnNames, rows);
      this.dataSource = new MatTableDataSource<any>([]);

      this.spinnerService.spinnerShow = false;
    });
  }

  formatDateNew(date: any) {
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
  * Populate the table with metadata
  */
  getGraphTable() {
    this.tableDescription = "";  
    this.dimUnit = "";
    if (this.dataset) {
      this.spinnerLoading = true; 
      const data = {
        idMeta: this.datasetId,
        dimensions: this.dataset.dimensions,
        lat: this.latlng.lat,
        lng: this.latlng.lng,
        dateStart: this.formatDateNew(this.dateStart),
        dateEnd: this.formatDateNew(this.dateEnd),
        variable: this.variable,
        range: this.range ? Math.abs(this.range) : null
      };

      this.httpService.post('dataset/getDataTableNew/', data).subscribe({
        next: (response: any) => {
          if (response.data !== "fuoriWms") {
            if (typeof response === 'string') {
              response = JSON.parse(response);
            }

            this.dataTable = response;
            this.displayedColumns = this.dataTable.data.table.columnNames;
            this.dimUnit = this.dataTable.data.table.columnUnits[this.dataTable.data.table.columnUnits.length - 1];

            if (this.dimUnit && this.dimUnit !== "No" && this.dimUnit !== "Value not defined" && typeof this.dimUnit === "string") {
              this.displayedColumns[this.displayedColumns.length - 1] =
                this.displayedColumns[this.displayedColumns.length - 1] + " [" + this.dimUnit + "]";
            } else {
              this.dimUnit = "";
            }

            const arr1: any[] = [];
            this.dataTable.data.table.rows.forEach((arr: any) => {
              const objArr: any = {};
              this.dataTable.data.table.columnNames.forEach((key: any, i: number) => {
                objArr[key] = arr[i];
              });
              arr1.push(objArr);
            });
            this.dataTable.data.table.rows = [...arr1];

            if (this.dataTable.data.table.rows.length > 0) {
              this.dataSource = new MatTableDataSource(this.dataTable.data.table.rows);
              this.setDataSourceAttributes();
            }
          } else {
            this.tableDescription = "The selected point is outside the WMS coverage";
            this.dataSource = new MatTableDataSource<any>([]);
            this.displayedColumns = [];
          }

          this.spinnerLoading = false; 
        },
        error: (err: any) => {
          console.error("Errore in getGraphTable:", err);
          this.spinnerLoading = false;
        }
      });
    }
  }

  createErddapUrl() {
    let prova: any[] = [];
    this.form.get("varSelected")?.value.map((el: any) => {
      prova = el;
    })

  }

  /**
  * Download a file directly from the ERDDAP platform using the generated URL with all required parameters
  */
  exportData(typeSel: any) {
    let erddapUrl: any;
    let latMin: any;
    let latMax: any;
    let lngMax: any;
    let lngMin: any;
    if (this.polygon) {
      const corner1 = this.polyExport.getSouthWest();
      const corner2 = this.polyExport.getNorthEast();

      // Get the latitudes and longitudes of the corners
      latMin = corner1.lat;
      lngMin = corner1.lng;
      latMax = corner2.lat;
      lngMax = corner2.lng;
    }
    if (this.dataset.griddap_url !== "") {
      erddapUrl = "https://erddap-adriaclim.cmcc-opa.eu/erddap/griddap/" + this.datasetId + typeSel + "?";
      let variable: any;
      this.form.get("varSelected")?.value.map((el: any, index: number) => {

        if (index === this.form.get("varSelected")?.value.length || index === 0) {
          variable = el;
        }
        else {

          variable = "," + el;

        }

        if (this.dataset.dimensions === 3) {
          if (this.polygon) {
            erddapUrl += variable + "%5B(" + this.formatDateExport(this.minValue) + "):1:(" + this.formatDateExport(this.maxValue) + ")%5D%5B(" + latMin + "):1:(" + latMax + ")%5D%5B(" + lngMin + "):1:(" + lngMax + ")%5D"

          }
          else {
            erddapUrl += variable + "%5B(" + this.formatDateExport(this.minValue) + "):1:(" + this.formatDateExport(this.maxValue) + ")%5D%5B(" + this.latlng.lat + "):1:(" + this.latlng.lat + ")%5D%5B(" + this.latlng.lng + "):1:(" + this.latlng.lng + ")%5D"
          }
        }
        else {
          if (this.minRange === undefined || this.maxRange === undefined) {
            this.minRange = 0
            this.maxRange = 0
          }
          const rangeMin = this.minRange;
          const rangeMax = this.maxRange;
          if (this.polygon) {
            erddapUrl += variable + "%5B(" + this.formatDateExport(this.minValue) + "):1:(" + this.formatDateExport(this.maxValue) + ")%5D%5B(" + rangeMin + "):1:(" + rangeMax + ")%5D%5B(" + latMin + "):1:(" + latMax + ")%5D%5B(" + lngMin + "):1:(" + lngMax + ")%5D"
          }
          else {
            erddapUrl += variable + "%5B(" + this.formatDateExport(this.minValue) + "):1:(" + this.formatDateExport(this.maxValue) + ")%5D%5B(" + rangeMin + "):1:(" + rangeMax + ")%5D%5B(" + this.latlng.lat + "):1:(" + this.latlng.lat + ")%5D%5B(" + this.latlng.lng + "):1:(" + this.latlng.lng + ")%5D"

          }
        }

      });
    } else {
      erddapUrl = "https://erddap-adriaclim.cmcc-opa.eu/erddap/tabledap/" + this.datasetId + typeSel + "?";
      const variable_names = this.dataset.variable_names.split(" ");
      variable_names.forEach((variable: any, index: any) => {
        if (index === variable_names.length - 1) {
          erddapUrl += variable;
        } else {
          erddapUrl += variable + "%2C";
        }
      });
      if (this.polygon) {
        erddapUrl += "&time%3E=" + this.formatDateExport(this.minValue) + "&time%3C=" + this.formatDateExport(this.maxValue) + "&latitude%3E=" + latMin + "&latitude%3C=" + latMax + "&longitude%3E=" + lngMin + "&longitude%3C=" + lngMax;
      }
      else {
        erddapUrl += "&time%3E=" + this.formatDateExport(this.minValue) + "&time%3C=" + this.formatDateExport(this.maxValue) + "&latitude%3E=" + this.latlng.lat + "&latitude%3C=" + this.latlng.lat + "&longitude%3E=" + this.latlng.lng + "&longitude%3C=" + this.latlng.lng;

      }

    }

    const link = document.createElement('a');
    link.setAttribute('target', '_self');
    link.setAttribute('href', erddapUrl);
    link.setAttribute('download', `${this.datasetId}${typeSel}`);
    document.body.appendChild(link);
    link.click();
    link.remove();

  }

  addDataTimeExport(graph: any) {
    const timestampArray = graph.map((element: any) => {
      if (element.x.indexOf("T") > -1) {
        element.x = this.formatDate(new Date(element.x));
      }
      const dateParts = element.x.split('/');

      const date = new Date(Number(dateParts[2]), Number(dateParts[1]) - 1, Number(dateParts[0]));
      return date;
    });

    this.minValue = timestampArray[0].getTime();
    this.maxValue = timestampArray[timestampArray.length - 1].getTime();

    this.options = {
      floor: this.dateStart.getTime(),
      ceil: this.dateEnd.getTime(),
      draggableRange: true,
      noSwitching: true,
      stepsArray: timestampArray.map((date: Date) => {
        return { value: date.getTime() };
      }),
      translate: (value: number, label: LabelType): string => {
        return new Date(value).toLocaleDateString('it-IT');
      },
    };

  }

  dataTablePolygon(event: any) {
    this.dataTable = event;
    this.displayedColumns = Object.keys(this.dataTable[0]);
    const lastCol = this.displayedColumns[this.displayedColumns.length - 1];
    this.dimUnit = this.dataTable[0][this.displayedColumns[this.displayedColumns.length - 1]];

    if (this.dimUnit && this.dimUnit !== "No" && this.dimUnit !== "Value not defined" && typeof this.dimUnit === "string") {
      this.displayedColumns[this.displayedColumns.length - 1] = this.displayedColumns[this.displayedColumns.length - 1] + " [" + this.dimUnit + "]";
    }

    let objArr: any = {};
    const arr1: any = [];
    this.dataTable.forEach((arr: any, index: number) => {
      if (index !== 0) {
        objArr = {};
        this.displayedColumns.forEach((key: any, i: number) => {
          if (i === this.displayedColumns.length - 1) {
            objArr[key] = arr[lastCol];
          } else {
            objArr[key] = arr[key];
          }
        })
        arr1.push(objArr);
      }

    });
    this.dataTable = [...arr1];
    this.dataTable.sort((a: any, b: any) => {
      return new Date(a.time).getTime() - new Date(b.time).getTime();
    });

    if (this.dataTable.length > 0) {
      this.dataSource = new MatTableDataSource(this.dataTable);
      // bypass ngIf for paginator
      this.setDataSourceAttributes();

    }
  }

  /**
  * Receive the spinnerLoading value from the child component
  */
  spinnerLoadingChild(event: any) {

    this.spinnerLoading = event;
  }

  /**
  * Receive statistics values from the child component for dataset comparison
  * and populate an object
  */
  compareStats(event: any) {
    this.stats = {
      meanDiffAvg: parseFloat(event.meanDiffAvg).toFixed(5),
      meanDiffAvgAbs: parseFloat(event.meanDiffAvgAbs).toFixed(5),
      rootSquaredDiff: parseFloat(event.rootSquaredDiff).toFixed(5),
    };
  }

  /**
  * Receive the error from the child component, assign it to the description,
  * and display it in the modal
  */
  descriptionError(event: any) {
    this.description = event;
  }

  /**
  * Receive the calculated statistics values from the child component
  * for the dataset displayed in the chart
  */
  meanMedianStdev(event: any) {
  // If null/empty, clear stats so the UI can hide them
    if (!event || typeof event !== 'string') {
      this.expoFormat(null);
      return;
    }

    const mean_median_stdev = event.split("_");
    this.expoFormat(mean_median_stdev);
  }

  /**
  * Receive values from the child component that control
  * the loading progress bar progression
  */
  progressBar(event: any) {
    if (this.isFakeActive) {
      if (this.fakeProgressInterval) {
        clearInterval(this.fakeProgressInterval);
        this.fakeProgressInterval = null;
      }
      this.isFakeActive = false;
    }

    this.progress = Number(event) || 0;
    this.progressWidth = this.progress + "%";
    this.progressBarAtStart = true;
  }

  progressBarCanvas(event: any) {
    if (this.isFakeActive) return; 
    this.progressBarAtStart = !!event;
  }

  startFakeProgress() {
    console.log("[PADRE] startFakeProgress eseguito");
    this.isFakeActive = true;
    this.fakeProgressStartedAt = Date.now();
    this.progressBarAtStart = true;
    this.progress = 0;
    this.progressWidth = "0%";
    if (this.fakeProgressInterval) {
      clearInterval(this.fakeProgressInterval);
    }

    this.fakeProgressInterval = setInterval(() => {
      if (!this.isFakeActive) return; 
      if (this.progress < 90) {
        this.progress += 5;
        this.progressWidth = this.progress + "%";
      }
    }, 150);
  }

  stopFakeProgress() {
    this.isFakeActive = false;

    if (this.fakeProgressInterval) {
      clearInterval(this.fakeProgressInterval);
      this.fakeProgressInterval = null;
    }
    // IMPORTANT: stop any previous "step to 100%" animation
    if (this.fakeProgressStepInterval) {
      clearInterval(this.fakeProgressStepInterval);
      this.fakeProgressStepInterval = null;
    }

    // If already hidden, do nothing (idempotent)
    if (!this.progressBarAtStart) {
      return;
    }

    // Jump to at least 95%
    if (this.progress < 95) {
      this.progress = 95;
      this.progressWidth = this.progress + "%";
    }

    // Animate last part to 100%
    this.fakeProgressStepInterval = setInterval(() => {
      if (this.progress < 100) {
        this.progress += 1;
        this.progressWidth = this.progress + "%";
      } else {
        clearInterval(this.fakeProgressStepInterval);
        this.fakeProgressStepInterval = null;

        setTimeout(() => {
          this.progressBarAtStart = false;
          this.progress = 0;
          this.progressWidth = "0%";
        }, 500);
      }
    }, 10);
  }




  /**
  * Format statistics values using x10^ notation
  * when numbers are too large or too small
  */
  expoFormat(mean_median_stdev: any) {
    // If stats are not meaningful (e.g. single timestamp case), clear them
    if (!mean_median_stdev || !Array.isArray(mean_median_stdev) || mean_median_stdev.length < 4) {
      this.meanValue = null;
      this.medianValue = null;
      this.stdevValue = null;
      this.trendValue = null;
      return;
    }
    this.meanValue = Number(mean_median_stdev[0]).toFixed(3);
    this.medianValue = Number(mean_median_stdev[1]).toFixed(3);
    this.stdevValue = Number(mean_median_stdev[2]).toFixed(3);
    this.trendValue = Number(mean_median_stdev[3]).toFixed(3);
    if (this.meanValue > 10000 || this.meanValue < 0.001 && this.meanValue != 0) {
      this.meanValue = parseFloat(mean_median_stdev[0]).toExponential().replace(/e\+?/, ' x 10^').replace(/(\d+\.\d{3})\d*/, '$1');
    }
    if (this.medianValue > 10000 || this.medianValue < 0.001 && this.medianValue != 0) {
      this.medianValue = parseFloat(mean_median_stdev[1]).toExponential().replace(/e\+?/, ' x 10^').replace(/(\d+\.\d{3})\d*/, '$1');
    }
    if (this.stdevValue > 10000 || this.stdevValue < 0.001 && this.stdevValue != 0) {
      this.stdevValue = parseFloat(mean_median_stdev[2]).toExponential().replace(/e\+?/, ' x 10^').replace(/(\d+\.\d{3})\d*/, '$1');
    }
    if (this.trendValue > 10000 || this.trendValue < 0.001 && this.trendValue != 0) {
      this.trendValue = parseFloat(mean_median_stdev[3]).toExponential().replace(/e\+?/, ' x 10^').replace(/(\d+\.\d{3})\d*/, '$1');
    }
    this.meanValue = parseFloat(mean_median_stdev[0]).toExponential().replace(/e\+?/, ' x 10^').replace(/(\d+\.\d{3})\d*/, '$1');
    this.medianValue = parseFloat(mean_median_stdev[1]).toExponential().replace(/e\+?/, ' x 10^').replace(/(\d+\.\d{3})\d*/, '$1');
    this.stdevValue = parseFloat(mean_median_stdev[2]).toExponential().replace(/e\+?/, ' x 10^').replace(/(\d+\.\d{3})\d*/, '$1');

    this.trendValue = parseFloat(mean_median_stdev[3]).toExponential().replace(/e\+?/, ' x 10^').replace(/(\d+\.\d{3})\d*/, '$1');
    if (this.meanValue.includes("x 10^0")) {
      this.meanValue = this.meanValue.replace("x 10^0", "");

    }
    if (this.medianValue.includes("x 10^0")) {
      this.medianValue = this.medianValue.replace("x 10^0", "");

    }
    if (this.stdevValue.includes("x 10^0")) {
      this.stdevValue = this.stdevValue.replace("x 10^0", "");

    }
    if (this.trendValue.includes("x 10^0")) {
      this.trendValue = this.trendValue.replace("x 10^0", "");
    }

  }

  /**
  * Assign the operation and statistic selected by the user
  */
  sendSelGraphPoly() {
    this.progressBarAtStart = false;
    this.spinnerService.spinnerShow = false;

    this.operation = this.form.get('operationSel')?.value;
    this.statistic  = this.form.get('statisticSel')?.value;
    this.isUpdate = true;
    setTimeout(() => { this.isUpdate = false; }, 0); 
  }


  statisticCalc(event: any) {
    this.statCalc = event;
  }

  /**
  * Update statistics for the dataset displayed in the chart
  */
  calcStatistics() {
    const data = {
      dates: this.statCalc.dates,
      values: this.statCalc.values,
      dataset: this.dataset,
      polygon: this.polygon,
    }

    if (this.statCalc.values.length > 0) {
      this.httpService.post('dataset/updateStatistics/', data).subscribe({
        next: (res: any) => {
          const mean_median_stdev = [res.newValues.mean, res.newValues.median, res.newValues.stdev, res.newValues.trend];
          this.expoFormat(mean_median_stdev);
        },

        error: (err: any) => {
          console.log(err);
        }
      });
    }

  }

  parseInFloatLat() {
    let floatLat = _.cloneDeep(this.latlng.lat);

    floatLat = parseFloat(floatLat);
    return floatLat.toFixed(5);
  }

  parseInFloatLng() {

    let floatLng = _.cloneDeep(this.latlng.lng);
    floatLng = parseFloat(floatLng);
    return floatLng.toFixed(5);
  }

}

