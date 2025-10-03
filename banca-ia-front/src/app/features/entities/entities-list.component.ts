import { Component } from '@angular/core';
import { EntityService } from '../../services/entity.service';
import { SubjectService } from '../../services/subject.service';
import { EntityDef } from '../../models/entity.model';

@Component({
  selector: 'app-entities-list',
  templateUrl: './entities-list.component.html'
})
export class EntitiesListComponent {
  displayedColumns = ['name','subjectId','patterns','gazetteer','actions'];
  data: EntityDef[] = [];
  subjects: Record<string,string> = {};
  constructor(private svc: EntityService, private subjectsApi: SubjectService) {}
  ngOnInit(){ this.subjectsApi.list().subscribe(ss => { ss.forEach(s => this.subjects[s.id!] = s.name); this.load(); }); }
  load(){ this.svc.list().subscribe(d => this.data = d); }
  remove(id?: string){ if (!id) return; if (confirm('Excluir entidade?')) this.svc.delete(id).subscribe(()=>this.load()); }
  sName(id: string){ return this.subjects[id] ?? id; }
}
