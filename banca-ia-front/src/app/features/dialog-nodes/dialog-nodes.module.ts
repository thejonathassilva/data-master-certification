import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormsModule } from '@angular/forms';
import { MaterialModule } from '../../shared/material.module';
import { DialogNodesRoutingModule } from './dialog-nodes-routing.module';
import { DialogNodesListComponent } from './dialog-nodes-list.component';
import { DialogNodesFormComponent } from './dialog-nodes-form.component';

@NgModule({
  declarations: [DialogNodesListComponent, DialogNodesFormComponent],
  imports: [CommonModule, ReactiveFormsModule, FormsModule, MaterialModule, DialogNodesRoutingModule]
})
export class DialogNodesModule {}
