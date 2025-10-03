export interface Intent {
  id?: string;
  subjectId: string;
  name: string;
  examples: string[];
  active: boolean;
}
