import { Component } from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { ChannelService } from '../../services/channel.service';

@Component({
  selector: 'app-channels-form',
  templateUrl: './channels-form.component.html'
})
export class ChannelsFormComponent {
  id = this.route.snapshot.paramMap.get('id');
  form = this.fb.group({
    name: ['', Validators.required],
    minConfSubject: [0.6, [Validators.required, Validators.min(0), Validators.max(1)]]
  });

  constructor(private fb: FormBuilder, private route: ActivatedRoute, private router: Router, private api: ChannelService) {}

  ngOnInit(){ if (this.id) this.api.get(this.id).subscribe(c => this.form.patchValue(c)); }
  save(){
    const p = this.id ? this.api.update(this.id!, this.form.value as any) : this.api.create(this.form.value as any);
    p.subscribe(() => this.router.navigateByUrl('/channels'));
  }
}
