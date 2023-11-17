import { DatePipe } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Component, ElementRef, Inject, ViewChild, ChangeDetectorRef, AfterContentChecked, OnInit, ViewEncapsulation, Renderer2, AfterViewInit } from '@angular/core';
import { FormBuilder, FormControl, FormGroup, Validators } from '@angular/forms';
import { MatDialogRef, MAT_DIALOG_DATA, MatDialog, MatDialogConfig } from '@angular/material/dialog';
import { MatSelect } from '@angular/material/select';
import * as _ from 'lodash';
import { GeoportalMapDialogComponent } from 'src/app/geoportal-map/geoportal-map-dialog/geoportal-map-dialog.component';
import { HttpService } from 'src/app/services/http.service';

@Component({
  selector: 'app-geoportal-map-menu-dialog',
  templateUrl: './geoportal-map-menu-dialog.component.html',
  styleUrls: ['./geoportal-map-menu-dialog.component.scss'],
  encapsulation: ViewEncapsulation.None
})
export class GeoportalMapMenuDialogComponent implements OnInit, AfterViewInit {

  @ViewChild('quartoMatSelect') quartoMatSelect!: MatSelect;
  @ViewChild("searchInput") searchInput: ElementRef | undefined;

  activeLayersArray: any;
  form!: FormGroup;
  isIndicator!: boolean;
  firstDatasetVariables: any[] = [];
  secondDatasetVariables: any[] = [];
  compareObj: any;

  firstValue: any = 100;
  secondValue: any = 100;


  // Nuove
  categoryDatasets: any;
  scaleDatasets: any;
  timeperiodDatasets: any;
  menuDatasets: any;
  resAllNodes: any;

  searchFilter: any;

  resultMenuDialog: any;

  constructor(
    private changeDetector: ChangeDetectorRef,
    private httpService: HttpService,
    public datePipe: DatePipe,
    private httpClient: HttpClient,private fb: FormBuilder,
    private dialogRef: MatDialogRef<GeoportalMapMenuDialogComponent>,
    private renderer: Renderer2,
    private dialog: MatDialog,
    @Inject(MAT_DIALOG_DATA) data: any){
      this.compareObj = data.compareObj;
      this.resultMenuDialog = data.resultMenuDialog;

      this.form = this.fb.group({
        category: new FormControl(null, Validators.required),
        scale: new FormControl(null, Validators.required),
        timeperiod: new FormControl(null, Validators.required),
        menu: new FormControl(null, Validators.required),
      });

      this.getAllNodes();

    }
  ngAfterViewInit(): void {

  }

  changeHeight() {
    const panel = document.querySelector('.mat-mdc-select-panel');
    if(panel) {
      this.renderer.setStyle(panel, 'height', '400px'); // Sostituisci con l'altezza desiderata
      // this.renderer.setStyle(panel, 'max-height', '100vh'); // Sostituisci con l'altezza desiderata
    }
  }

  async ngOnInit() {

    // this.dialogRef.updateSize('fit-content', '60%');
    // this.chargeAll()
    // setTimeout(() => {
    // this.checkDimensions();

    // }, 500);

  }

  close() {
      this.dialogRef.close("");
  }

  /**
   * Funzione che torna dei dati alla chiusura della modale tramite il bottone ok
   */
  ok(){

    if(this.form.get("menu")?.value) {
      let data = {
        menu: this.form.get("menu")?.value,
        category: this.form.get("category")?.value,
        scale: this.form.get("scale")?.value,
        timeperiod: this.form.get("timeperiod")?.value
      }
      this.dialogRef.close(data);

    }

  }

  /**
   * Funzione che richiama tutti i nuovi dataset di erddap attraverso i servizi api collegati ai nodi del database
   */
  getAllNodes() {
    this.categoryDatasets = [];

    let tmpCategoryDatasets: any[] = [];
    let tmpScale: any[] = [];
    let tmpTimeperiods: any[] = [];

    this.httpService.post('test/allNodes', {
    }).subscribe({
      next: (res: any) => {

        this.resAllNodes = res.nodes;

        this.resAllNodes.forEach((element: any) => {
          if(element.adriaclim_dataset !== "no" && element.adriaclim_dataset !== "No" && element.adriaclim_dataset !== "Indicator") {
            tmpCategoryDatasets.push(element.adriaclim_dataset);
          }
        });
        this.categoryDatasets = [...new Set(tmpCategoryDatasets)];
        this.form.get("category")?.setValue([this.categoryDatasets[0]]);


        this.resAllNodes.forEach((el: any) => {
          if(el.adriaclim_dataset === this.form.get("category")?.value[0]) {
            tmpScale.push(el.adriaclim_scale);
          }
        });
        this.scaleDatasets = [...new Set(tmpScale)];
        this.form.get("scale")?.setValue([this.scaleDatasets[0]]);

        this.resAllNodes.forEach((el: any) => {
          if (el.adriaclim_dataset === this.form.get("category")?.value[0] && el.adriaclim_scale === this.form.get("scale")?.value[0]) {
            tmpTimeperiods.push(el.adriaclim_timeperiod);
          }
        });
        this.timeperiodDatasets = [...new Set(tmpTimeperiods)];
        this.form.get("timeperiod")?.setValue([this.timeperiodDatasets[0]]);

        if(this.resultMenuDialog) {
          this.form.get("category")?.setValue(this.resultMenuDialog.category);
          this.form.get("scale")?.setValue(this.resultMenuDialog.scale);
          this.form.get("timeperiod")?.setValue(this.resultMenuDialog.timeperiod);
        }
        // this.menuDatasets = this.resAllNodes.filter((el: any) => {
        //   el.adriaclim_dataset === this.form.get("category")?.value && el.adriaclim_scale === this.form.get("scale")?.value && el.adriaclim_timeperiod === this.form.get("timeperiod")?.value
        //   const categoryMatch = this.form.get("category")?.value.every((category: any) => category === el.adriaclim_dataset);
        //   const scaleMatch = this.form.get("scale")?.value.every((scale: any) => scale === el.adriaclim_scale);
        //   const timeperiodMatch = this.form.get("timeperiod")?.value.every((timeperiod: any) => timeperiod === el.adriaclim_timeperiod);
        //   return categoryMatch && scaleMatch && timeperiodMatch;
        // });
        let condizione1: any;
        let condizione2: any;
        let condizione3: any;
        this.menuDatasets = this.resAllNodes.filter((el: any) => {
          condizione1 = this.form.get("category")?.value.includes(el.adriaclim_dataset);
          condizione2 = this.form.get("scale")?.value.includes(el.adriaclim_scale);
          condizione3 = this.form.get("timeperiod")?.value.includes(el.adriaclim_timeperiod);
          return condizione1 && condizione2 && condizione3;
        });

        this.searchFilter = this.menuDatasets;

      },
      error: (msg: any) => {
        console.log("SUB ERROR");

        console.log('ALL NODES ERROR: ', msg);
      }
    })
    // this.dataSource.data = TREE_DATA;

  }

  setFilter() {
    // this.searchInput!.nativeElement.value = '';
    if(this.searchInput) {
      if(this.searchInput.nativeElement.value && this.searchInput.nativeElement.value !== "") {

        this.onKey(this.searchInput.nativeElement.value);

      }
    }
  }

  /**
   * Funzione che cambia dinamicamente gli elementi all'interno dei vari menu
   */
  changeSel(type?: string) {
    // this.menuDatasets = [];
    // this.searchFilter = [];
    this.searchInput!.nativeElement.value = '';
    let tmpScale: any[] = [];
    let tmpTimeperiods: any[] = [];

    if(type === "c") {

      this.resAllNodes.forEach((el: any) => {

        this.form.get("category")?.value.forEach((cat: any) => {
          if(cat === el.adriaclim_dataset) {
            tmpScale.push(el.adriaclim_scale);

          }

        });

      });
      // this.scaleDatasets = [];
      // this.timeperiodDatasets = [];
      this.scaleDatasets = [...new Set(tmpScale)];
      this.form.get("scale")?.setValue([this.scaleDatasets[0]]);

      this.resAllNodes.forEach((el: any) => {
        this.form.get("category")?.value.forEach((cat: any) => {

          if(cat === el.adriaclim_dataset && this.form.get("scale")?.value[0] === el.adriaclim_scale) {
            tmpTimeperiods.push(el.adriaclim_timeperiod);

          }

        });

      });
      // this.timeperiodDatasets = [];

      this.timeperiodDatasets = [...new Set(tmpTimeperiods)];

      this.form.get("timeperiod")?.setValue([this.timeperiodDatasets[0]]);
      let condizione1: any;
      let condizione2: any;
      let condizione3: any;

      this.menuDatasets = this.resAllNodes.filter((el: any) => {
        condizione1 = this.form.get("category")?.value.includes(el.adriaclim_dataset);
        condizione2 = this.form.get("scale")?.value[0] === el.adriaclim_scale;
        condizione3 = this.form.get("timeperiod")?.value[0] === el.adriaclim_timeperiod;
        return condizione1 && condizione2 && condizione3;
      });

    }
    else if(type === "s") {
      this.resAllNodes.forEach((el: any) => {
        this.form.get("category")?.value.forEach((cat: any) => {
          this.form.get("scale")?.value.forEach((scale: any) => {
            if(cat === el.adriaclim_dataset && scale === el.adriaclim_scale) {
              tmpTimeperiods.push(el.adriaclim_timeperiod);

            }

          })

        })
      });
      this.timeperiodDatasets = [...new Set(tmpTimeperiods)];

      this.form.get("timeperiod")?.setValue([this.timeperiodDatasets[0]]);

      let condizione1: any;
      let condizione2: any;
      let condizione3: any;

      this.menuDatasets = this.resAllNodes.filter((el: any) => {
        condizione1 = this.form.get("category")?.value.includes(el.adriaclim_dataset);
        condizione2 = this.form.get("scale")?.value.includes(el.adriaclim_scale);
        condizione3 = this.form.get("timeperiod")?.value.includes(el.adriaclim_timeperiod);
        return condizione1 && condizione2 && condizione3;
      });

    }
    else if(type === "t") {
      let condizione1: any;
      let condizione2: any;
      let condizione3: any;
      this.menuDatasets = this.resAllNodes.filter((el: any) => {
        condizione1 = this.form.get("category")?.value.includes(el.adriaclim_dataset);
        condizione2 = this.form.get("scale")?.value.includes(el.adriaclim_scale);
        condizione3 = this.form.get("timeperiod")?.value.includes(el.adriaclim_timeperiod);
        return condizione1 && condizione2 && condizione3;
      });

    }

    this.searchFilter = this.menuDatasets;

  }

  /**
   * Funzione chiamata al key up che va a chiamare la funzione search
   */
  onKey(event: any) {
    if(event) {
      this.searchFilter = this.search(event.target.value);

    }
    else if(typeof event === "string" && event !== "") {
      this.searchFilter = this.search(event);
    }
    else {
      this.searchFilter = this.search(null);
    }

    }

  /**
   * Funzione che permette di effettuare una ricerca tra i vari dataset
   */
  search(value: any) {
    if(value) {
      let filters = value.toLowerCase().split(" ");
      let menuDatasetClone = _.cloneDeep(this.menuDatasets);
      let menuFiltered = menuDatasetClone.filter((option: any) => {
        let optionTitle = option.title.toLowerCase();
        let optionInstitution = option.institution.toLowerCase();
        return filters.every((filter: any) => {

          if(optionTitle.includes(filter)) {
            return optionTitle
          }
          else if(optionInstitution.includes(filter)) {
            return optionInstitution
          }

        });
      });
      return menuFiltered;

    }
    else {

      return this.menuDatasets;
    }
  }

  /**
   * Funzione che apre la modale contenente la tabella dei metadati del dataset selezionato
   */
  openTableDialog(idMeta?: any, title?: any, n?: any) {

    let dataId: any;

    if (!idMeta) {
      if (this.form.get("menu")?.value.id) {
      dataId = this.form.get("menu")?.value.id;
      }
      else if (this.form.get("menu")?.value.dataset_id) {
        dataId = this.form.get("menu")?.value.dataset_id;
      }
    }

    const dialogConfig = new MatDialogConfig();

    dialogConfig.disableClose = true;
    dialogConfig.autoFocus = true;

    dialogConfig.data = {
      success: true,
      datasetId: idMeta ? idMeta : dataId,
      datasetName: title ? title : this.form.get("menu")?.value.title,
    };

    const dialogRef = this.dialog.open(GeoportalMapDialogComponent, dialogConfig);

  }

  /**
   * Funzione che resetta i filtri impostandoli tutti vuoti
   */
  resetFilters() {
    this.form.get("category")?.setValue([]);
    this.form.get("scale")?.setValue([]);
    this.form.get("timeperiod")?.setValue([]);
    this.form.get("menu")?.setValue(null);
    this.searchInput!.nativeElement.value = '';
  }

}
