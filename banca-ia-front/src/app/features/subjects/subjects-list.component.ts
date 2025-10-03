import { Component } from '@angular/core';
import { SubjectService } from '../../services/subject.service';
import { ChannelService } from '../../services/channel.service';
import { Subject } from '../../models/subject.model';
import { Channel } from '../../models/channel.model';

@Component({
  selector: 'app-subjects-list',
  templateUrl: './subjects-list.component.html'
})
export class SubjectsListComponent {
  displayedColumns = ['name','channelId','activeModelVersion','intentMinConf','entityMinConf','actions'];
  data: Subject[] = [];
  channels: Record<string,string> = {};

  constructor(private svc: SubjectService, private channelsApi: ChannelService) {}
  ngOnInit(){
    this.channelsApi.list().subscribe(cs => {
      cs.forEach(c => this.channels[c.id!] = c.name);
      this.load();
    });
  }
  load(){ this.svc.list().subscribe(d => this.data = d); }
  remove(id?: string){ if (!id) return; if (confirm('Excluir assunto?')) this.svc.delete(id).subscribe(()=>this.load()); }
  nameOfChannel(id: string){ return this.channels[id] ?? id; }
}
