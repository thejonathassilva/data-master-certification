export type TrainScope = 'subject' | 'channel' | 'both';
export type VersioningStrategy = 'auto' | 'increment' | 'fixed';

export interface TrainRequest {
  scope: TrainScope;
  subject_id: string;
  channel?: string;                 // opcional: BFF pode preencher
  versioning_strategy: VersioningStrategy;
  base_version?: string | null;
  base_lang_model?: string | null;
  requested_by?: string;
  notes?: string;
  correlation_id: string;
}
