import { Component } from '@angular/core';
import { IntentService } from '../../services/intent.service';
import { SubjectService } from '../../services/subject.service';
import { Intent } from '../../models/intent.model';
import { Subject } from '../../models/subject.model';

@Component({
  selector: 'app-intents-list',
  templateUrl: './intents-list.component.html'
})
export class IntentsListComponent {
  displayedColumns = ['name','subjectId','active','examples','actions'];
  data: Intent[] = [];
  subjects: Record<string,string> = {};

  constructor(private svc: IntentService, private subjectsApi: SubjectService) {}
  ngOnInit(){
    this.subjectsApi.list().subscribe(ss => { ss.forEach(s => this.subjects[s.id!] = s.name); this.load(); });
  }
  load(){ this.svc.list().subscribe(d => this.data = d); }
  remove(id?: string){ if (!id) return; if (confirm('Excluir intenção?')) this.svc.delete(id).subscribe(()=>this.load()); }
  sName(id: string){ return this.subjects[id] ?? id; }
}
