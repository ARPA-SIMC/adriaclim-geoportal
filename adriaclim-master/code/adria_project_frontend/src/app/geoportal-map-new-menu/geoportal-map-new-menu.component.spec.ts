import { ComponentFixture, TestBed } from '@angular/core/testing';

import { GeoportalMapNewMenuComponent } from './geoportal-map-new-menu.component';

describe('GeoportalMapNewMenuComponent', () => {
  let component: GeoportalMapNewMenuComponent;
  let fixture: ComponentFixture<GeoportalMapNewMenuComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ GeoportalMapNewMenuComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(GeoportalMapNewMenuComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
