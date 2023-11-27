import { ComponentFixture, TestBed } from '@angular/core/testing';

import { GeoportalMapMenuDialogComponent } from './geoportal-map-menu-dialog.component';

describe('GeoportalMapMenuDialogComponent', () => {
  let component: GeoportalMapMenuDialogComponent;
  let fixture: ComponentFixture<GeoportalMapMenuDialogComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ GeoportalMapMenuDialogComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(GeoportalMapMenuDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
