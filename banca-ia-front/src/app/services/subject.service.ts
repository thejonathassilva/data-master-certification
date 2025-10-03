import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { API_BASE } from '../core/api.config';
import { Subject } from '../models/subject.model';
import { TrainRequest } from '../models/train.model';
import { Observable } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class SubjectService {
  private base = `${API_BASE}/subjects`;
  constructor(private http: HttpClient) {}
  list(channelId?: string): Observable<Subject[]> {
    const url = channelId ? `${this.base}?channelId=${encodeURIComponent(channelId)}` : this.base;
    return this.http.get<Subject[]>(url);
  }
  get(id: string): Observable<Subject> { return this.http.get<Subject>(`${this.base}/${id}`); }
  create(data: Subject): Observable<Subject> { return this.http.post<Subject>(this.base, data); }
  update(id: string, data: Partial<Subject>): Observable<Subject> { return this.http.put<Subject>(`${this.base}/${id}`, data); }
  delete(id: string) { return this.http.delete(`${this.base}/${id}`); }
  train(id: string, body: TrainRequest) {
    return this.http.post(`${this.base}/${id}/train`, body, { headers: { 'X-User':'console' } });
  }
}
