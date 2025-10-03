import { Component } from '@angular/core';
import { FormArray, FormBuilder, FormControl, Validators } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { MatDialog } from '@angular/material/dialog';
import { IntentService } from '../../services/intent.service';
import { SubjectService } from '../../services/subject.service';
import { PreviewService } from '../../services/preview.service';
import { Subject } from '../../models/subject.model';
import { PreviewIntentDialogComponent } from './preview-intent-dialog.component';

@Component({
  selector: 'app-intents-form',
  templateUrl: './intents-form.component.html'
})
export class IntentsFormComponent {
  id = this.route.snapshot.paramMap.get('id');
  subjects: Subject[] = [];
  loadingPreview = false;

  form = this.fb.group({
    subjectId: ['', Validators.required],
    name: ['', Validators.required],
    active: [true],
    examples: this.fb.array<FormControl<string>>([
      this.fb.control('', { nonNullable: true, validators: [Validators.required] })
    ])
  });

  get examplesFA(): FormArray<FormControl<string>> {
    return this.form.controls['examples'] as FormArray<FormControl<string>>;
  }

  constructor(
    private fb: FormBuilder,
    private route: ActivatedRoute,
    private router: Router,
    private svc: IntentService,
    private subjectsApi: SubjectService,
    private preview: PreviewService,
    private dialog: MatDialog
  ) {}

  ngOnInit() {
    this.subjectsApi.list().subscribe(ss => (this.subjects = ss));
    if (this.id) {
      this.svc.get(this.id).subscribe(i => {
        this.form.patchValue({ subjectId: i.subjectId, name: i.name, active: i.active });
        while (this.examplesFA.length) this.examplesFA.removeAt(0);
        (i.examples?.length ? i.examples : ['']).forEach(txt =>
          this.examplesFA.push(this.fb.control(txt, { nonNullable: true, validators: [Validators.required] }))
        );
      });
    }
  }

  addExample(afterIndex?: number) {
    const ctrl = this.fb.control('', { nonNullable: true, validators: [Validators.required] });
    const idx = typeof afterIndex === 'number' ? afterIndex + 1 : this.examplesFA.length;
    this.examplesFA.insert(idx, ctrl);
  }

  removeExample(index: number) {
    if (this.examplesFA.length <= 1) return;
    this.examplesFA.removeAt(index);
  }

  private buildPayload() {
    const raw = this.form.getRawValue();
    const examples = this.examplesFA.controls.map(c => c.value.trim()).filter(Boolean);
    return {
      subjectId: raw.subjectId!,
      name: raw.name!,
      active: !!raw.active,
      examples
    };
  }

  save() {
    if (this.form.invalid) { this.form.markAllAsTouched(); return; }
    const payload = this.buildPayload();
    const req = this.id ? this.svc.update(this.id!, payload) : this.svc.create(payload);
    req.subscribe(() => this.router.navigateByUrl('/intents'));
  }

  previewIntent() {
    if (this.form.invalid) { this.form.markAllAsTouched(); return; }
    const payload = this.buildPayload();
    if (!payload.examples.length) return alert('Adicione pelo menos 1 exemplo.');

    this.loadingPreview = true;
    this.preview.intentPreview({
      subjectId: payload.subjectId,
      intentDraft: { name: payload.name, examples: payload.examples }
    }).subscribe({
      next: (res) => {
        this.loadingPreview = false;
        this.dialog.open(PreviewIntentDialogComponent, {
          data: { result: res, draftName: payload.name },
          width: '720px'
        });
      },
      error: () => { this.loadingPreview = false; }
    });
  }
}
