// src/app/shared/shared.module.ts
import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MaterialModule } from './material.module';
import { ThemeToggleComponent } from './theme-toggle.component';

@NgModule({
  declarations: [ThemeToggleComponent],
  imports: [CommonModule, MaterialModule],
  exports: [ThemeToggleComponent, MaterialModule]
})
export class SharedModule {}
