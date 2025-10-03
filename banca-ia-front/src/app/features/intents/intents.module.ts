import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormsModule } from '@angular/forms';
import { MaterialModule } from '../../shared/material.module';
import { IntentsRoutingModule } from './intents-routing.module';
import { IntentsListComponent } from './intents-list.component';
import { IntentsFormComponent } from './intents-form.component';

@NgModule({
  declarations: [IntentsListComponent, IntentsFormComponent],
  imports: [CommonModule, ReactiveFormsModule, FormsModule, MaterialModule, IntentsRoutingModule]
})
export class IntentsModule {}
