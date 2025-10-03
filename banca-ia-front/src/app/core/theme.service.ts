// src/app/core/theme.service.ts
import { Injectable } from '@angular/core';

type Mode = 'light' | 'dark';
const STORAGE_KEY = 'banca-ia-theme';

@Injectable({ providedIn: 'root' })
export class ThemeService {
  private mode: Mode = 'light';

  constructor() {
    const saved = (localStorage.getItem(STORAGE_KEY) as Mode) || null;
    const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    this.mode = saved ?? (prefersDark ? 'dark' : 'light');
    this.apply();
  }

  get current(): Mode { return this.mode; }

  toggle() {
    this.mode = this.mode === 'light' ? 'dark' : 'light';
    localStorage.setItem(STORAGE_KEY, this.mode);
    this.apply();
  }

  private apply() {
    document.body.classList.remove('theme-light', 'theme-dark');
    document.body.classList.add(this.mode === 'light' ? 'theme-light' : 'theme-dark');
  }
}
