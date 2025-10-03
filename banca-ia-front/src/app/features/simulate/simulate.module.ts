import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule } from '@angular/forms';
import { MaterialModule } from '../../shared/material.module';
import { SimulateRoutingModule } from './simulate-routing.module';
import { SimulateComponent } from './simulate.component';

@NgModule({
  declarations: [SimulateComponent],
  imports: [CommonModule, ReactiveFormsModule, MaterialModule, SimulateRoutingModule]
})
export class SimulateModule {}
