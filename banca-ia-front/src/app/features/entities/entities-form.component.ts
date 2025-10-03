import { Component } from '@angular/core';
import { FormArray, FormBuilder, FormControl, Validators } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { EntityService } from '../../services/entity.service';
import { SubjectService } from '../../services/subject.service';
import { Subject } from '../../models/subject.model';

@Component({
  selector: 'app-entity-form',
  templateUrl: './entities-form.component.html'
})
export class EntitiesFormComponent {
  id = this.route.snapshot.paramMap.get('id');
  subjects: Subject[] = [];

  form = this.fb.group({
    subjectId: ['', Validators.required],
    name: ['', Validators.required],
    patterns: this.fb.array<FormControl<string>>([
      this.fb.control('', { nonNullable: true, validators: [Validators.required] })
    ]),
    gazetteer: this.fb.array<FormControl<string>>([
      this.fb.control('', { nonNullable: true })
    ])
  });

  get patternsFA(): FormArray<FormControl<string>> {
    return this.form.controls['patterns'] as FormArray<FormControl<string>>;
  }
  get gazetteerFA(): FormArray<FormControl<string>> {
    return this.form.controls['gazetteer'] as FormArray<FormControl<string>>;
  }

  constructor(
    private fb: FormBuilder,
    private route: ActivatedRoute,
    private router: Router,
    private svc: EntityService,
    private subjectsApi: SubjectService
  ) {}

  ngOnInit() {
    this.subjectsApi.list().subscribe(ss => (this.subjects = ss));

    if (this.id) {
      this.svc.get(this.id).subscribe(e => {
        this.form.patchValue({ subjectId: e.subjectId, name: e.name });
        // patterns
        while (this.patternsFA.length) this.patternsFA.removeAt(0);
        (e.patterns?.length ? e.patterns : ['']).forEach(p =>
          this.patternsFA.push(this.fb.control(p, { nonNullable: true, validators: [Validators.required] }))
        );
        // gazetteer
        while (this.gazetteerFA.length) this.gazetteerFA.removeAt(0);
        (e.gazetteer?.length ? e.gazetteer : ['']).forEach(g =>
          this.gazetteerFA.push(this.fb.control(g, { nonNullable: true }))
        );
      });
    }
  }

  addPattern(after?: number) {
    const idx = typeof after === 'number' ? after + 1 : this.patternsFA.length;
    this.patternsFA.insert(idx, this.fb.control('', { nonNullable: true, validators: [Validators.required] }));
  }
  removePattern(i: number) {
    if (this.patternsFA.length <= 1) return;
    this.patternsFA.removeAt(i);
  }

  addGaz(after?: number) {
    const idx = typeof after === 'number' ? after + 1 : this.gazetteerFA.length;
    this.gazetteerFA.insert(idx, this.fb.control('', { nonNullable: true }));
  }
  removeGaz(i: number) {
    if (this.gazetteerFA.length <= 1) return;
    this.gazetteerFA.removeAt(i);
  }

  private buildPayload() {
    const raw = this.form.getRawValue();
    const patterns = this.patternsFA.controls.map(c => c.value.trim()).filter(Boolean);
    const gazetteer = this.gazetteerFA.controls.map(c => c.value.trim()).filter(Boolean);
    return {
      subjectId: raw.subjectId!,
      name: raw.name!,
      patterns,
      gazetteer
    };
  }

  save() {
    if (this.form.invalid) { this.form.markAllAsTouched(); return; }
    const payload = this.buildPayload();
    const req = this.id ? this.svc.update(this.id!, payload) : this.svc.create(payload);
    req.subscribe(() => this.router.navigateByUrl('/entities'));
  }
}
