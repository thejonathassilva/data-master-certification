import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse, HttpHeaders } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { catchError, map } from 'rxjs/operators';
import { API_BASE } from '../core/api.config';
import { PredictionResponse } from '../models/predict.model';

type Engine = 'spacy-IA' | 'stick-IA';

@Injectable({ providedIn: 'root' })
export class PredictService {
  constructor(private http: HttpClient) {}

  predict(engine: Engine, channel: string, text: string): Observable<PredictionResponse> {
    let url = '';
    let body: any = {};

    url  = `${API_BASE}/predict?channel=${encodeURIComponent(channel)}`;
    body = { text };
    const headers = this.buildHeaders(engine);

    return this.http.post<any>(url, body, { headers }).pipe(
      map(resp => this.normalize(engine, resp)),
      catchError((err: HttpErrorResponse) => {
        const fb: PredictionResponse = {
          subjectId: null,
          intentId: null,
          confidence: 0,
          entities: [],
          _fallback: true as any,
          _message: 'Precisa de mais treinamento, intenção não encontrada'
        };
        return of(fb);
      })
    );
  }

  private buildHeaders(engine: Engine): HttpHeaders {
    const ia = engine === 'spacy-IA' ? 'spacy' : 'J_assistant';
    return new HttpHeaders({
      'Content-Type': 'application/json',
      'IA': ia
    });
  }

  private normalize(engine: Engine, resp: any): PredictionResponse {
    if (engine === 'spacy-IA') {
      return {
        subjectId: resp?.subjectId ?? null,
        intentId:  resp?.intentId ?? null,
        confidence: Number(resp?.confidence ?? 0),
        entities: Array.isArray(resp?.entities) ? resp.entities : [],
        node: resp?.node
      };
    }

    const intentId =
      resp?.intentId ??
      resp?.intent ??
      resp?.prediction?.intent ??
      null;

    const confidence = Number(
      resp?.confidence ??
      resp?.score ??
      resp?.prediction?.score ??
      0
    );

    const entitiesSrc =
      resp?.entities ??
      resp?.prediction?.entities ??
      [];

    const entities = Array.isArray(entitiesSrc)
      ? entitiesSrc.map((e: any) => ({
          label: e.label ?? e.type ?? e.entity ?? '',
          value: e.value ?? e.text ?? '',
          start: e.start ?? e.begin,
          end:   e.end,
          score: e.score ?? e.confidence
        }))
      : [];

    const subjectId = resp?.subjectId ?? null;

    return { subjectId, intentId, confidence, entities, node: resp?.node };
  }
}
