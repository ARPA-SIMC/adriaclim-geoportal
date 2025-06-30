import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CanvasGraphComponent } from './canvas-graph.component';

describe('CanvasGraphComponent', () => {
  let component: CanvasGraphComponent;
  let fixture: ComponentFixture<CanvasGraphComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ CanvasGraphComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CanvasGraphComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
