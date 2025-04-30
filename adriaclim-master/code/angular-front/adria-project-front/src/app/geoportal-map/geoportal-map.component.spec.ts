import { ComponentFixture, TestBed } from '@angular/core/testing';

import { GeoportalMapComponent } from './geoportal-map.component';

describe('GeoportalMapComponent', () => {
  let component: GeoportalMapComponent;
  let fixture: ComponentFixture<GeoportalMapComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ GeoportalMapComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(GeoportalMapComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
