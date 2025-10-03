import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { SubjectsListComponent } from './subjects-list.component';
import { SubjectsFormComponent } from './subjects-form.component';

const routes: Routes = [
  { path: '', component: SubjectsListComponent },
  { path: 'new', component: SubjectsFormComponent },
  { path: ':id', component: SubjectsFormComponent },
];

@NgModule({ imports: [RouterModule.forChild(routes)], exports: [RouterModule] })
export class SubjectsRoutingModule {}
