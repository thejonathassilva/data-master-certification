import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { CommonModule } from '@angular/common';
import { MaterialModule } from '../../shared/material.module';
import { PreviewResponse } from '../../models/predict.model';

@Component({
  selector: 'app-preview-intent-dialog',
  standalone: true,
  imports: [CommonModule, MatDialogModule, MaterialModule],
  templateUrl: './preview-intent-dialog.component.html'
})
export class PreviewIntentDialogComponent {
  constructor(
    @Inject(MAT_DIALOG_DATA) public data: { result: PreviewResponse; draftName: string },
    public ref: MatDialogRef<PreviewIntentDialogComponent>
  ) {}
  close(){ this.ref.close(); }
}
