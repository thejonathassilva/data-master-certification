// src/app/shared/material.module.ts
import { NgModule } from '@angular/core';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatTabsModule } from '@angular/material/tabs';
import { MatTableModule } from '@angular/material/table';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatChipsModule } from '@angular/material/chips';
import { MatIconModule } from '@angular/material/icon';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatDividerModule } from '@angular/material/divider';
import { MatDialogModule } from '@angular/material/dialog';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatListModule } from '@angular/material/list';

const modules = [
  MatToolbarModule, MatTabsModule, MatTableModule, MatButtonModule,
  MatFormFieldModule, MatInputModule, MatSelectModule, MatChipsModule,
  MatIconModule, MatSlideToggleModule, MatTooltipModule, MatDividerModule,
  MatDialogModule, MatProgressSpinnerModule, MatListModule
];

@NgModule({ exports: modules })
export class MaterialModule {}
