import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { API_BASE } from '../core/api.config';
import { EntityDef } from '../models/entity.model';

@Injectable({ providedIn: 'root' })
export class EntityService {
  private base = `${API_BASE}/entities`;
  constructor(private http: HttpClient) {}
  list(subjectId?: string): Observable<EntityDef[]> {
    const url = subjectId ? `${this.base}?subjectId=${encodeURIComponent(subjectId)}` : this.base;
    return this.http.get<EntityDef[]>(url);
  }
  get(id: string): Observable<EntityDef> { return this.http.get<EntityDef>(`${this.base}/${id}`); }
  create(data: EntityDef): Observable<EntityDef> { return this.http.post<EntityDef>(this.base, data); }
  update(id: string, data: Partial<EntityDef>): Observable<EntityDef> { return this.http.put<EntityDef>(`${this.base}/${id}`, data); }
  delete(id: string) { return this.http.delete(`${this.base}/${id}`); }
}
