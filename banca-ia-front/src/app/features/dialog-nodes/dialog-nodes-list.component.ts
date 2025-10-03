import { Component } from '@angular/core';
import { DialogNodeService } from '../../services/dialog-node.service';
import { SubjectService } from '../../services/subject.service';
import { DialogNode } from '../../models/dialog-node.model';

@Component({
  selector: 'app-dialog-nodes-list',
  templateUrl: './dialog-nodes-list.component.html'
})
export class DialogNodesListComponent {
  displayedColumns = ['name','subjectId','condition','response','children','actions'];
  data: DialogNode[] = [];
  subjects: Record<string,string> = {};
  constructor(private svc: DialogNodeService, private subjectsApi: SubjectService) {}
  ngOnInit(){ this.subjectsApi.list().subscribe(ss => { ss.forEach(s => this.subjects[s.id!] = s.name); this.load(); }); }
  load(){ this.svc.list().subscribe(d => this.data = d); }
  remove(id?: string){ if (!id) return; if (confirm('Excluir nó?')) this.svc.delete(id).subscribe(()=>this.load()); }
  sName(id: string){ return this.subjects[id] ?? id; }
}
