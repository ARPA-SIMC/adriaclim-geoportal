import { DatePipe } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Component, ElementRef, Inject, ViewChild, ChangeDetectorRef, AfterContentChecked, OnInit, ViewEncapsulation, Renderer2, AfterViewInit } from '@angular/core';
import { FormBuilder, FormControl, FormGroup, Validators } from '@angular/forms';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { MatSelect } from '@angular/material/select';
import { HttpService } from 'src/app/services/http.service';

@Component({
  selector: 'app-geoportal-map-menu-dialog',
  templateUrl: './geoportal-map-menu-dialog.component.html',
  styleUrls: ['./geoportal-map-menu-dialog.component.scss'],
  encapsulation: ViewEncapsulation.None
})
export class GeoportalMapMenuDialogComponent implements OnInit, AfterViewInit {

  @ViewChild('quartoMatSelect') quartoMatSelect!: MatSelect;

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

  constructor(
    private changeDetector: ChangeDetectorRef,
    private httpService: HttpService,
    public datePipe: DatePipe,
    private httpClient: HttpClient,
    private fb: FormBuilder,
    private dialogRef: MatDialogRef<GeoportalMapMenuDialogComponent>,
    private renderer: Renderer2,
    @Inject(MAT_DIALOG_DATA) data: any){
      // this.activeLayersArray = data.activeLayersArray;
      // this.categoryDatasets = data.categoryDatasets,
      // this.scaleDatasets = data.scaleDatasets,
      // this.timeperiodDatasets = data.timeperiodDatasets,
      // this.menuDatasets = data.menuDatasets,
      this.compareObj = data.compareObj;
      this.form = this.fb.group({
        category: new FormControl(),
        scale: new FormControl(),
        timeperiod: new FormControl(),
        menu: new FormControl(),
      });

      this.getAllNodes();

    }
  ngAfterViewInit(): void {
    if(this.quartoMatSelect) {
      this.changeHeight();
    }
    // this.quartoMatSelect.openedChange.subscribe((opened) => {
    //   if (opened) {
    //     const panel = document.querySelector('.mat-mdc-select-panel');
    //     if (panel) {
    //       this.renderer.setStyle(panel, 'min-height', '700px'); // Sostituisci con l'altezza desiderata
    //     }
    //   }
    // });
  }

  changeHeight() {
    const panel = document.querySelector('.mat-mdc-select-panel');
    if(panel) {
      this.renderer.setStyle(panel, 'min-height', '400px'); // Sostituisci con l'altezza desiderata
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

  ok(){
    // let data = {
    //   firstDataset: this.form.get('firstDataset')?.value,
    //   secondDataset: this.form.get('secondDataset')?.value,
    //   firstVarSel: this.form.get('variableFirstData')?.value,
    //   secondVarSel: this.form.get('variableSecondData')?.value,
    // }
    // this.dialogRef.close(data);

    this.dialogRef.close("ok");

  }

  /**
   * FUNZIONE CHE RICHIAMA TUTTI I NUOVI DATASET DI ERDDAP ATTRAVERSO I SERVIZI API COLLEGATI AI NODI DEL DATABASE
   */
  getAllNodes() {
    this.categoryDatasets = [];

    let tmpCategoryDatasets: any[] = [];
    let tmpScale: any[] = [];
    let tmpTimeperiods: any[] = [];

    this.httpService.post('test/allNodes', {
    }).subscribe({
      next: (res: any) => {
        // console.log("SUB NEXT");
        // console.log("RES NODES =", res.nodes);

        this.resAllNodes = res.nodes;

        this.resAllNodes.forEach((element: any) => {
          if(element.adriaclim_dataset !== "no" && element.adriaclim_dataset !== "No" && element.adriaclim_dataset !== "Indicator") {
            tmpCategoryDatasets.push(element.adriaclim_dataset);
          }
        });
        this.categoryDatasets = [...new Set(tmpCategoryDatasets)];
        this.form.get("category")?.setValue([this.categoryDatasets[0]]);
        console.log("FORM CATEGORY ALLO START =", this.form.get("category")?.value);


        this.resAllNodes.forEach((el: any) => {
          if(el.adriaclim_dataset === this.form.get("category")?.value[0]) {
            tmpScale.push(el.adriaclim_scale);
          }
        });
        this.scaleDatasets = [...new Set(tmpScale)];
        this.form.get("scale")?.setValue([this.scaleDatasets[0]]);
        console.log("FORM SCALE ALLO START =", this.form.get("scale")?.value);

        this.resAllNodes.forEach((el: any) => {
          if (el.adriaclim_dataset === this.form.get("category")?.value[0] && el.adriaclim_scale === this.form.get("scale")?.value[0]) {
            tmpTimeperiods.push(el.adriaclim_timeperiod);
          }
        });
        this.timeperiodDatasets = [...new Set(tmpTimeperiods)];
        this.form.get("timeperiod")?.setValue([this.timeperiodDatasets[0]]);
        console.log("FORM TIMEPERIOD ALLO START =", this.form.get("timeperiod")?.value);

        this.menuDatasets = this.resAllNodes.filter((el: any) => {
          el.adriaclim_dataset === this.form.get("category")?.value && el.adriaclim_scale === this.form.get("scale")?.value && el.adriaclim_timeperiod === this.form.get("timeperiod")?.value
          const categoryMatch = this.form.get("category")?.value.every((category: any) => category === el.adriaclim_dataset);
          const scaleMatch = this.form.get("scale")?.value.every((scale: any) => scale === el.adriaclim_scale);
          const timeperiodMatch = this.form.get("timeperiod")?.value.every((timeperiod: any) => timeperiod === el.adriaclim_timeperiod);
          return categoryMatch && scaleMatch && timeperiodMatch;
        });

        this.searchFilter = this.menuDatasets;

        // console.log("SEARCH FILTER =", this.searchFilter);


      },
      error: (msg: any) => {
        console.log("SUB ERROR");

        console.log('ALL NODES ERROR: ', msg);
      }
    })
    // this.dataSource.data = TREE_DATA;

  }

  /**
   * Funzione che cambia dinamicamente gli elementi all'interno dei vari menu
   */
  changeSel(type?: string) {
    console.log("FORM =", this.form.get("category")?.value);


    let tmpScale: any[] = [];
    let tmpTimeperiods: any[] = [];

    if(type === "c") {
      console.log("CATEGORY?");

      this.resAllNodes.forEach((el: any) => {
        // console.log("FORM CATEGORY =", this.form.get("category")?.value[0]);

        this.form.get("category")?.value.every((cat: any) => {
          if(cat === el.adriaclim_dataset) {
            console.log("CONTROLLO OK");
            tmpScale.push(el.adriaclim_scale);

          }

        });

      });
      this.scaleDatasets = [...new Set(tmpScale)];
      console.log("SCALE DATASETS =", this.scaleDatasets);

      this.form.get("scale")?.setValue([this.scaleDatasets[0]]);

      this.resAllNodes.forEach((el: any) => {
        this.form.get("category")?.value.every((cat: any) => {
          this.form.get("scale")?.value.every((scale: any) => {
            if(cat === el.adriaclim_dataset && scale === el.adriaclim_scale) {
              tmpTimeperiods.push(el.adriaclim_timeperiod);
            }

          });

        });

      });
      this.timeperiodDatasets = [...new Set(tmpTimeperiods)];
      this.form.get("timeperiod")?.setValue([this.timeperiodDatasets[0]]);
      let categoryMatch: any;
      let scaleMatch: any;
      let timeperiodMatch: any;

      this.menuDatasets = this.resAllNodes.filter((el: any) => {
        // el.adriaclim_dataset === this.form.get("category")?.value && el.adriaclim_scale === this.form.get("scale")?.value && el.adriaclim_timeperiod === this.form.get("timeperiod")?.value
        // categoryMatch = this.form.get("category")?.value.every((category: any) => category === el.adriaclim_dataset);
        // scaleMatch = this.form.get("scale")?.value.every((scale: any) => scale === el.adriaclim_scale);
        // timeperiodMatch = this.form.get("timeperiod")?.value.every((timeperiod: any) => timeperiod === el.adriaclim_timeperiod);
        // return categoryMatch && scaleMatch && timeperiodMatch;
        this.form.get("category")?.value.forEach((cat: any) => {
          this.form.get("scale")?.value.forEach((scale: any) => {
            this.form.get("timeperiod")?.value.forEach((timeperiod: any) => {
              if(cat === el.adriaclim_dataset && scale === el.adriaclim_scale && timeperiod === el.adriaclim_timeperiod) {
                categoryMatch = true;
                scaleMatch = true;
                timeperiodMatch = true;
              }
            });
          });
        });
        return categoryMatch && scaleMatch && timeperiodMatch;
      });
      console.log("CATEGORY MATCH =", categoryMatch);
      console.log("SCALE MATCH =", scaleMatch);
      console.log("TIMEPERIOD MATCH =", timeperiodMatch);


    }
    else if(type === "s") {
      this.resAllNodes.forEach((el: any) => {
        this.form.get("category")?.value.every((cat: any) => {
          this.form.get("scale")?.value.every((scale: any) => {
            if(cat === el.adriaclim_dataset && scale === el.adriaclim_scale) {
              tmpTimeperiods.push(el.adriaclim_timeperiod);

            }

          })

        })
      });
      this.timeperiodDatasets = [...new Set(tmpTimeperiods)];
      this.form.get("timeperiod")?.setValue([this.timeperiodDatasets[0]]);

    }
    else if(type === "t") {
      let categoryMatch: any;
      let scaleMatch: any;
      let timeperiodMatch: any;
      this.menuDatasets = this.resAllNodes.filter((el: any) => {
        // el.adriaclim_dataset === this.form.get("category")?.value && el.adriaclim_scale === this.form.get("scale")?.value && el.adriaclim_timeperiod === this.form.get("timeperiod")?.value
        // const categoryMatch = this.form.get("category")?.value.every((category: any) => category === el.adriaclim_dataset);
        // const scaleMatch = this.form.get("scale")?.value.every((scale: any) => scale === el.adriaclim_scale);
        // const timeperiodMatch = this.form.get("timeperiod")?.value.every((timeperiod: any) => timeperiod === el.adriaclim_timeperiod);
        // return categoryMatch && scaleMatch && timeperiodMatch;
        this.form.get("category")?.value.forEach((cat: any) => {
          this.form.get("scale")?.value.forEach((scale: any) => {
            this.form.get("timeperiod")?.value.forEach((timeperiod: any) => {
              if(cat === el.adriaclim_dataset && scale === el.adriaclim_scale && timeperiod === el.adriaclim_timeperiod) {
                categoryMatch = true;
                scaleMatch = true;
                timeperiodMatch = true;
              }

            });
          });
        });
        return categoryMatch && scaleMatch && timeperiodMatch;
      });

    }

    this.searchFilter = this.menuDatasets;
  }

  /**
   * Funzione chiamata al key up che va a chiamare la funzione search
   */
  onKey(event: any) {
    // console.log("EVENT =", event.target.value);

    this.searchFilter = this.search(event.target.value);
    // console.log("SEARCH FILTER DOPO FILTRO =", this.searchFilter);


    }

  /**
   * Funzione che permette di effettuare una ricerca tra i vari dataset
   */
  search(value: string) {
    if(value) {
      let filters = value.toLowerCase().split(" ");

      let menuFiltered = this.menuDatasets.filter((option: any) => {
        let optionTitle = option.title.toLowerCase();
        let optionInstitution = option.institution.toLowerCase();
        return filters.every((filter: any) => {
          // console.log("FILTER =", filter);
          // console.log("OPTION TITLE =", optionTitle.includes(filter));
          // console.log("OPTION INSTITUTION =", optionInstitution.includes(filter));

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


}
