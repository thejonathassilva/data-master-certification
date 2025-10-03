import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { ChannelsListComponent } from './channels-list.component';
import { ChannelsFormComponent } from './channels-form.component';

const routes: Routes = [
  { path: '', component: ChannelsListComponent },
  { path: 'new', component: ChannelsFormComponent },
  { path: ':id', component: ChannelsFormComponent },
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class ChannelsRoutingModule {}
