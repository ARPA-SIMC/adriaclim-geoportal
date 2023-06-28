import { Component, Inject } from '@angular/core';
import { HttpService } from '../services/http.service';
import { FormBuilder, FormControl, FormGroup, Validators } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';

@Component({
  selector: 'app-select-coords-dialog',
  templateUrl: './select-coords-dialog.component.html',
  styleUrls: ['./select-coords-dialog.component.scss']
})
export class SelectCoordsDialogComponent {

  selectCoords: any;
  coordsForm: FormGroup;

  constructor(
    private httpService: HttpService,
    private fb: FormBuilder,
    private dialogRef: MatDialogRef<SelectCoordsDialogComponent>,
    @Inject(MAT_DIALOG_DATA) data: any) {
    this.selectCoords = data.selectCoords;
    this.coordsForm = this.fb.group({
      // lat: new FormControl(null, [Validators.required, Validators.pattern("^[0-9]*$"), Validators.min(-90), Validators.max(90)]),
      lat: new FormControl(null, [Validators.required, Validators.pattern("^[0-9]+(\.[0-9]+)?$"), Validators.min(-90), Validators.max(90)]),
      lng: new FormControl(null, [Validators.required, Validators.pattern("^[0-9]+(\.[0-9]+)?$"), Validators.min(-180), Validators.max(180)]),
    });

  }

  compareDatasets() {
    let data = {
      lat: this.coordsForm.get('lat')?.value,
      lng: this.coordsForm.get('lng')?.value,
    }
    this.dialogRef.close(data);

  }

  close() {
    this.dialogRef.close("");
  }

}
