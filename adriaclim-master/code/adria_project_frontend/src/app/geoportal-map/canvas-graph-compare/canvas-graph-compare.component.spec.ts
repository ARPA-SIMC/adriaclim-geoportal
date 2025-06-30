import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CanvasGraphCompareComponent } from './canvas-graph-compare.component';

describe('CanvasGraphCompareComponent', () => {
  let component: CanvasGraphCompareComponent;
  let fixture: ComponentFixture<CanvasGraphCompareComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ CanvasGraphCompareComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CanvasGraphCompareComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
