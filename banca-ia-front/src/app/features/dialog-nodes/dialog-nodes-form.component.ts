import { Component } from '@angular/core';
import { FormArray, FormBuilder, FormControl, Validators } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { DialogNodeService } from '../../services/dialog-node.service';
import { SubjectService } from '../../services/subject.service';
import { DialogNode, ConditionType } from '../../models/dialog-node.model';
import { Subject } from '../../models/subject.model';

@Component({
  selector: 'app-dialog-nodes-form',
  templateUrl: './dialog-nodes-form.component.html'
})
export class DialogNodesFormComponent {
  id = this.route.snapshot.paramMap.get('id');
  subjects: Subject[] = [];

  form = this.fb.group({
    subjectId: this.fb.nonNullable.control<string>('', { validators: [Validators.required] }),
    name:      this.fb.nonNullable.control<string>('', { validators: [Validators.required] }),
    conditionType: this.fb.nonNullable.control<ConditionType>('intent', { validators: [Validators.required] }),
    conditionValue: this.fb.control<string | null>(''),
    responseText:   this.fb.control<string | null>(''),

    responseActions: this.fb.array<FormControl<string>>([
      this.fb.control('', { nonNullable: true })
    ]),
    children: this.fb.array<FormControl<string>>([
      this.fb.control('', { nonNullable: true })
    ])
  });

  // atalhos
  get actionsFA(): FormArray<FormControl<string>> {
    return this.form.controls['responseActions'] as FormArray<FormControl<string>>;
  }
  get childrenFA(): FormArray<FormControl<string>> {
    return this.form.controls['children'] as FormArray<FormControl<string>>;
  }

  constructor(
    private fb: FormBuilder,
    private route: ActivatedRoute,
    private router: Router,
    private svc: DialogNodeService,
    private subjectsApi: SubjectService
  ) {}

  ngOnInit(){
    this.subjectsApi.list().subscribe(ss => this.subjects = ss);

    if (this.id) {
      this.svc.get(this.id).subscribe((n: any) => {
        // normaliza type
        const rawType = n?.conditionType ?? 'intent';
        const safeType: ConditionType =
          rawType === 'intent' || rawType === 'expr' || rawType === 'true' ? rawType : 'intent';

        this.form.patchValue({
          subjectId: n.subjectId,
          name: n.name,
          conditionType: safeType,
          conditionValue: n.conditionValue ?? '',
          responseText: n.responseText ?? ''
        });

        // arrays
        const acts: string[] = Array.isArray(n?.responseActions) ? n.responseActions : [];
        while (this.actionsFA.length) this.actionsFA.removeAt(0);
        (acts.length ? acts : ['']).forEach(a => this.actionsFA.push(this.fb.control(a ?? '', { nonNullable: true })));

        const kids: string[] = Array.isArray(n?.children) ? n.children : [];
        while (this.childrenFA.length) this.childrenFA.removeAt(0);
        (kids.length ? kids : ['']).forEach(c => this.childrenFA.push(this.fb.control(c ?? '', { nonNullable: true })));
      });
    }

    // se não tem condição, limpa o valor
    this.form.controls.conditionType.valueChanges.subscribe(v => {
      if (v === 'true') this.form.controls.conditionValue.setValue('');
    });
  }

  addAction(after?: number) {
    const idx = typeof after === 'number' ? after + 1 : this.actionsFA.length;
    this.actionsFA.insert(idx, this.fb.control('', { nonNullable: true }));
  }
  removeAction(i: number) {
    if (this.actionsFA.length <= 1) return;
    this.actionsFA.removeAt(i);
  }

  addChild(after?: number) {
    const idx = typeof after === 'number' ? after + 1 : this.childrenFA.length;
    this.childrenFA.insert(idx, this.fb.control('', { nonNullable: true }));
  }
  removeChild(i: number) {
    if (this.childrenFA.length <= 1) return;
    this.childrenFA.removeAt(i);
  }

  private buildPayload(): Omit<DialogNode, 'id'> {
    const raw = this.form.getRawValue();

    const responseActions = this.actionsFA.controls
      .map(c => (c.value ?? '').trim())
      .filter(Boolean);

    const children = this.childrenFA.controls
      .map(c => (c.value ?? '').trim())
      .filter(Boolean);

    return {
      subjectId: raw.subjectId,
      name: raw.name,
      conditionType: raw.conditionType as ConditionType,
      conditionValue: raw.conditionType === 'true' ? '' : (raw.conditionValue ?? '').trim(),
      responseText: (raw.responseText ?? '').trim(),
      responseActions,
      children
    };
  }


  save(){
    if (this.form.invalid) { this.form.markAllAsTouched(); return; }
    const payload = this.buildPayload();
    const req = this.id ? this.svc.update(this.id!, payload) : this.svc.create(payload);
    req.subscribe(() => this.router.navigateByUrl('/dialog-nodes'));
  }
}
