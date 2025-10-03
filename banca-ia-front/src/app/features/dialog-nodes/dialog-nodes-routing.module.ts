import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { DialogNodesListComponent } from './dialog-nodes-list.component';
import { DialogNodesFormComponent } from './dialog-nodes-form.component';

const routes: Routes = [
  { path: '', component: DialogNodesListComponent },
  { path: 'new', component: DialogNodesFormComponent },
  { path: ':id', component: DialogNodesFormComponent },
];

@NgModule({ imports: [RouterModule.forChild(routes)], exports: [RouterModule] })
export class DialogNodesRoutingModule {}
