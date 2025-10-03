import { Component } from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
import { v4 as uuidv4 } from './uuid';
import { ActivatedRoute, Router } from '@angular/router';
import { SubjectService } from '../../services/subject.service';
import { ChannelService } from '../../services/channel.service';
import { TrainRequest } from '../../models/train.model';
import { Channel } from '../../models/channel.model';

@Component({
  selector: 'app-subjects-form',
  templateUrl: './subjects-form.component.html'
})
export class SubjectsFormComponent {
  id = this.route.snapshot.paramMap.get('id');
  channels: Channel[] = [];
  subjectLoaded: any;
  langOptions = [
    { label: 'Português (BR)', value: 'pt_core_news_md' }
  ];

  form = this.fb.group({
    channelId: ['', Validators.required],
    name: ['', Validators.required],
    intentMinConf: [0.6],
    entityMinConf: [0.5],
    activeModelVersion: [''],

    train: this.fb.group({
    scope: ['both', Validators.required],
    versioning_strategy: ['auto', Validators.required],
    base_version: [''],
    base_lang_model: ['pt_core_news_md'],
    requested_by: ['console'],
    notes: ['']
  })
});

  constructor(private fb: FormBuilder, private route: ActivatedRoute, private router: Router,
              private svc: SubjectService, private channelsApi: ChannelService) {}

  ngOnInit(){
    this.channelsApi.list().subscribe(cs => this.channels = cs);
    if (this.id) this.svc.get(this.id).subscribe(s => this.form.patchValue(s));
  }

  save(){
    const p = this.id ? this.svc.update(this.id!, this.form.value as any) : this.svc.create(this.form.value as any);
    p.subscribe(() => this.router.navigateByUrl('/subjects'));
  }

  private findChannelNameById(id: string | null | undefined) {
    const c = this.channels.find(x => x.id === id);
    return c?.name;
  }

  private buildTrainPayload(subjectId: string): TrainRequest {
    const v = this.form.getRawValue();
    const t = v.train!;
    const channelName = this.findChannelNameById(v.channelId) || undefined;

    return {
      scope: t.scope as any,
      subject_id: subjectId,
      channel: channelName, // pode ser undefined; o BFF preenche se faltar
      versioning_strategy: t.versioning_strategy as any,
      base_version: t.base_version || null,
      base_lang_model: t.base_lang_model || null,
      requested_by: t.requested_by || 'console',
      notes: t.notes || '',
      correlation_id: uuidv4() 
    };
  }

  train() {
    if (!this.id) return alert('Salve o assunto antes de treinar.');
    const payload = this.buildTrainPayload(this.id);
    this.svc.train(this.id!, payload).subscribe(() => {
      alert('Treino enviado para a fila!');
    });
  }
}