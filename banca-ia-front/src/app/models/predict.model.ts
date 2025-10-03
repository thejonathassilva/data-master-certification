export interface PredictRequest { text: string; }
export interface EntityDTO {
  label: string; value: string;
  start?: number; end?: number; score?: number;
}

export interface PredictionResponse {
  subjectId: string | null;
  intentId: string | null;
  confidence: number;
  entities: EntityDTO[];
  node?: any;

  /** internos de UI (opcional) */
  _fallback?: boolean;
  _message?: string;
}

export interface PreviewRequest {
  subjectId: string;
  intentDraft: { name: string; examples: string[]; }
}
export interface PreviewResponse {
  deltaMetrics: { intent_f1_before: number; intent_f1_after: number; };
  sampleConfidence: { text: string; confidence: number; predictedIntent?: string }[];
  topConfusions: [string, string, number][];
}
