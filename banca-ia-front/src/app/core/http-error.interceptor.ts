import { Injectable } from '@angular/core';
import {
  HttpErrorResponse, HttpEvent, HttpHandler, HttpInterceptor, HttpRequest
} from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';

@Injectable()
export class HttpErrorInterceptor implements HttpInterceptor {
  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    const isPredict = req.url.includes('/api/predict');

    return next.handle(req).pipe(
      catchError((err: HttpErrorResponse) => {
        if (isPredict) {
          return throwError(() => err);
        }

        return throwError(() => err);
      })
    );
  }
}
