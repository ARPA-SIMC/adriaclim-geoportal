import { ComponentFixture, TestBed } from '@angular/core/testing';

import { GeoportalMapDialogComponent } from './geoportal-map-dialog.component';

describe('GeoportalMapDialogComponent', () => {
  let component: GeoportalMapDialogComponent;
  let fixture: ComponentFixture<GeoportalMapDialogComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ GeoportalMapDialogComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(GeoportalMapDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
