// src/app/shared/theme-toggle.component.ts
import { Component } from '@angular/core';
import { ThemeService } from '../core/theme.service';

@Component({
  selector: 'app-theme-toggle',
  template: `
    <div class="theme-toggle">
      <mat-icon aria-hidden="true">{{ service.current === 'dark' ? 'dark_mode' : 'light_mode' }}</mat-icon>
      <mat-slide-toggle
        [checked]="service.current==='dark'"
        (change)="service.toggle()"
        color="accent"
        aria-label="Alternar tema">
      </mat-slide-toggle>
    </div>
  `,
  styles: [`
    .theme-toggle { display:flex; align-items:center; gap:8px; }
    mat-icon { font-size:20px; width:20px; height:20px; }
  `]
})
export class ThemeToggleComponent {
  constructor(public service: ThemeService) {}
}
