import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { API_BASE } from '../core/api.config';
import { Observable } from 'rxjs';
import { Channel } from '../models/channel.model';

@Injectable({ providedIn: 'root' })
export class ChannelService {
  private base = `${API_BASE}/channels`;
  constructor(private http: HttpClient) {}
  list(): Observable<Channel[]> { return this.http.get<Channel[]>(this.base); }
  get(id: string): Observable<Channel> { return this.http.get<Channel>(`${this.base}/${id}`); }
  create(data: Channel): Observable<Channel> { return this.http.post<Channel>(this.base, data); }
  update(id: string, data: Partial<Channel>): Observable<Channel> { return this.http.put<Channel>(`${this.base}/${id}`, data); }
  delete(id: string) { return this.http.delete(`${this.base}/${id}`); }
}
