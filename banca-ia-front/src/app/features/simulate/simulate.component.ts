import { Component } from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
import { PredictService } from '../../services/predict.service';
import { PredictionResponse } from '../../models/predict.model';

type MsgRole = 'user' | 'bot';
type Msg = { role: MsgRole; text: string; meta?: PredictionResponse };
type Engine = 'spacy-IA' | 'stick-IA';

@Component({
  selector: 'app-simulate',
  templateUrl: './simulate.component.html',
  styles: [`
    .chat{display:flex;flex-direction:column;gap:12px}
    .bubble{padding:10px 12px;border-radius:12px}
    .user{background:#e3f2fd;align-self:flex-end}
    .bot{background:#f1f8e9}
  `]
})
export class SimulateComponent {
  constructor(private fb: FormBuilder, private predict: PredictService) {}

  channels = ['PF','PJ'];

  form = this.fb.group({
    channel: this.fb.nonNullable.control<string>('PF', [Validators.required]),
    engine:  this.fb.nonNullable.control<Engine>('spacy-IA'),
    text:    this.fb.nonNullable.control<string>('', [Validators.required])
  });

  history: Msg[] = [];

  send() {
    let { channel, engine, text } = this.form.getRawValue();
    if (!text.trim()) return;

    this.history.push({ role: 'user', text });

    this.predict.predict(engine, channel, text).subscribe(resp => {
      text = resp?.node?.text || 'Precisa de mais treinamento, intenção não encontrada';
      if ((resp as any)._fallback) {
        this.history.push({
          role: 'bot',
          text: (resp as any)._message || 'Precisa de mais treinamento, intenção não encontrada'
        });
        this.form.controls.text.setValue('');
        return;
      }

      this.history.push({ role: 'bot', text, meta: resp });
      this.form.controls.text.setValue('');
    });
  }
}
