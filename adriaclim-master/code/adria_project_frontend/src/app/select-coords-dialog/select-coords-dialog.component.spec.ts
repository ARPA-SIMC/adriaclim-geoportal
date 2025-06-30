import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SelectCoordsDialogComponent } from './select-coords-dialog.component';

describe('SelectCoordsDialogComponent', () => {
  let component: SelectCoordsDialogComponent;
  let fixture: ComponentFixture<SelectCoordsDialogComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ SelectCoordsDialogComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(SelectCoordsDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
