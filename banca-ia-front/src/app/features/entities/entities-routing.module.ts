import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { EntitiesListComponent } from './entities-list.component';
import { EntitiesFormComponent } from './entities-form.component';

const routes: Routes = [
  { path: '', component: EntitiesListComponent },
  { path: 'new', component: EntitiesFormComponent },
  { path: ':id', component: EntitiesFormComponent },
];

@NgModule({ imports: [RouterModule.forChild(routes)], exports: [RouterModule] })
export class EntitiesRoutingModule {}
