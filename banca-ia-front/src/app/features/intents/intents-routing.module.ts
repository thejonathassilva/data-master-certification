import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { IntentsListComponent } from './intents-list.component';
import { IntentsFormComponent } from './intents-form.component';

const routes: Routes = [
  { path: '', component: IntentsListComponent },
  { path: 'new', component: IntentsFormComponent },
  { path: ':id', component: IntentsFormComponent },
];

@NgModule({ imports: [RouterModule.forChild(routes)], exports: [RouterModule] })
export class IntentsRoutingModule {}
