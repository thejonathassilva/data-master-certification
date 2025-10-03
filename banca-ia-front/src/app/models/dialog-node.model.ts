export const CONDITION_TYPES = ['intent', 'expr', 'true'] as const;
export type ConditionType = typeof CONDITION_TYPES[number];

export interface DialogNode {
  id?: string;
  subjectId: string;
  name: string;
  conditionType: ConditionType | null;
  conditionValue?: string | null;
  responseText?: string | null;
  responseActions: string[];
  children: string[];
}
