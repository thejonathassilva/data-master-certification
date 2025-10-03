import { Component } from '@angular/core';
import { ChannelService } from '../../services/channel.service';
import { Channel } from '../../models/channel.model';

@Component({
  selector: 'app-channels-list',
  templateUrl: './channels-list.component.html'
})
export class ChannelsListComponent {
  displayedColumns = ['name', 'minConfSubject', 'actions'];
  data: Channel[] = [];
  constructor(private api: ChannelService) {}
  ngOnInit(){ this.load(); }
  load(){ this.api.list().subscribe(d => this.data = d); }
  remove(id?: string){ if (!id) return; if (confirm('Excluir canal?')) this.api.delete(id).subscribe(() => this.load()); }
}
