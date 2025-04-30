import { ComponentFixture, TestBed } from '@angular/core/testing';

import { GeoportalCompareDialogComponent } from './geoportal-compare-dialog.component';

describe('GeoportalCompareDialogComponent', () => {
  let component: GeoportalCompareDialogComponent;
  let fixture: ComponentFixture<GeoportalCompareDialogComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ GeoportalCompareDialogComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(GeoportalCompareDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
