import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { API_BASE } from '../core/api.config';
import { DialogNode } from '../models/dialog-node.model';

@Injectable({ providedIn: 'root' })
export class DialogNodeService {
  private base = `${API_BASE}/dialog-nodes`;
  constructor(private http: HttpClient) {}
  list(subjectId?: string): Observable<DialogNode[]> {
    const url = subjectId ? `${this.base}?subjectId=${encodeURIComponent(subjectId)}` : this.base;
    return this.http.get<DialogNode[]>(url);
  }
  get(id: string): Observable<DialogNode> { return this.http.get<DialogNode>(`${this.base}/${id}`); }
  create(data: Omit<DialogNode, 'id'>) {
    return this.http.post<DialogNode>(this.base, data);
  }
  update(id: string, data: Partial<DialogNode>): Observable<DialogNode> { return this.http.put<DialogNode>(`${this.base}/${id}`, data); }
  delete(id: string) { return this.http.delete(`${this.base}/${id}`); }
}
