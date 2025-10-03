import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormsModule } from '@angular/forms';
import { MaterialModule } from '../../shared/material.module';
import { EntitiesRoutingModule } from './entities-routing.module';
import { EntitiesListComponent } from './entities-list.component';
import { EntitiesFormComponent } from './entities-form.component';

@NgModule({
  declarations: [EntitiesListComponent, EntitiesFormComponent],
  imports: [CommonModule, ReactiveFormsModule, FormsModule, MaterialModule, EntitiesRoutingModule]
})
export class EntitiesModule {}
