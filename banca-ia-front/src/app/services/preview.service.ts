import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { API_BASE } from '../core/api.config';
import { Observable } from 'rxjs';
import { PreviewRequest, PreviewResponse } from '../models/predict.model';

@Injectable({ providedIn: 'root' })
export class PreviewService {
  constructor(private http: HttpClient) {}
  intentPreview(body: PreviewRequest): Observable<PreviewResponse> {
    return this.http.post<PreviewResponse>(`${API_BASE}/preview/intent`, body);
  }
}
