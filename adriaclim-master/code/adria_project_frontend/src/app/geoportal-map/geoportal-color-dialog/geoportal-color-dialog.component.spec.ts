import { ComponentFixture, TestBed } from '@angular/core/testing';

import { GeoportalColorDialogComponent } from './geoportal-color-dialog.component';

describe('GeoportalColorDialogComponent', () => {
  let component: GeoportalColorDialogComponent;
  let fixture: ComponentFixture<GeoportalColorDialogComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ GeoportalColorDialogComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(GeoportalColorDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
