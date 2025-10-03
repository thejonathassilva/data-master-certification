import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule } from '@angular/forms';
import { MaterialModule } from '../../shared/material.module';
import { SubjectsRoutingModule } from './subjects-routing.module';
import { SubjectsListComponent } from './subjects-list.component';
import { SubjectsFormComponent } from './subjects-form.component';

@NgModule({
  declarations: [SubjectsListComponent, SubjectsFormComponent],
  imports: [CommonModule, ReactiveFormsModule, MaterialModule, SubjectsRoutingModule]
})
export class SubjectsModule {}
