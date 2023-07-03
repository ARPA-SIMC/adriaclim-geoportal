import { ComponentFixture, TestBed } from '@angular/core/testing';

import { WelcomePageGeoportalComponent } from './welcome-page-geoportal.component';

describe('WelcomePageGeoportalComponent', () => {
  let component: WelcomePageGeoportalComponent;
  let fixture: ComponentFixture<WelcomePageGeoportalComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ WelcomePageGeoportalComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(WelcomePageGeoportalComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
