import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { API_BASE } from '../core/api.config';
import { Intent } from '../models/intent.model';

@Injectable({ providedIn: 'root' })
export class IntentService {
  private base = `${API_BASE}/intents`;
  constructor(private http: HttpClient) {}
  list(subjectId?: string): Observable<Intent[]> {
    const url = subjectId ? `${this.base}?subjectId=${encodeURIComponent(subjectId)}` : this.base;
    return this.http.get<Intent[]>(url);
  }
  get(id: string): Observable<Intent> { return this.http.get<Intent>(`${this.base}/${id}`); }
  create(data: Intent): Observable<Intent> { return this.http.post<Intent>(this.base, data); }
  update(id: string, data: Partial<Intent>): Observable<Intent> { return this.http.put<Intent>(`${this.base}/${id}`, data); }
  delete(id: string) { return this.http.delete(`${this.base}/${id}`); }
}
