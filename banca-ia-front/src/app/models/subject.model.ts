export interface Subject {
  id?: string;
  channelId: string;
  name: string;
  activeModelVersion?: string | null;
  intentMinConf?: number | null;
  entityMinConf?: number | null;
}
