import { ComponentFixture, TestBed } from '@angular/core/testing';

import { GeoportalMapNewComponent } from './geoportal-map-new.component';

describe('GeoportalMapNewComponent', () => {
  let component: GeoportalMapNewComponent;
  let fixture: ComponentFixture<GeoportalMapNewComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ GeoportalMapNewComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(GeoportalMapNewComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
