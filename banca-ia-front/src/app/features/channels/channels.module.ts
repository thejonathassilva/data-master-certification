import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule } from '@angular/forms';
import { MaterialModule } from '../../shared/material.module';
import { ChannelsRoutingModule } from './channels-routing.module';
import { ChannelsListComponent } from './channels-list.component';
import { ChannelsFormComponent } from './channels-form.component';

@NgModule({
  declarations: [ChannelsListComponent, ChannelsFormComponent],
  imports: [CommonModule, ReactiveFormsModule, MaterialModule, ChannelsRoutingModule]
})
export class ChannelsModule {}
