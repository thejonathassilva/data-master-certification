import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

const routes: Routes = [
  { path: '', redirectTo: 'simulate', pathMatch: 'full' },
  { path: 'channels', loadChildren: () => import('./features/channels/channels.module').then(m => m.ChannelsModule) },
  { path: 'subjects', loadChildren: () => import('./features/subjects/subjects.module').then(m => m.SubjectsModule) },
  { path: 'intents', loadChildren: () => import('./features/intents/intents.module').then(m => m.IntentsModule) },
  { path: 'entities', loadChildren: () => import('./features/entities/entities.module').then(m => m.EntitiesModule) },
  { path: 'dialog-nodes', loadChildren: () => import('./features/dialog-nodes/dialog-nodes.module').then(m => m.DialogNodesModule) },
  { path: 'simulate', loadChildren: () => import('./features/simulate/simulate.module').then(m => m.SimulateModule) },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule {}
