export interface PowerTagValueMeta {
  name: string;
  unit: string | null;
}

export interface PowerTagMetadata {
  panel: string | null;
  slug: string | null;
  component: string | null;
  consumer: string | null;
  /** Descriptors of the live value fields (units come from the AsyncAPI schema). */
  values: PowerTagValueMeta[];
}

export interface PowerTagValues {
  currentA: number | null;
  currentB: number | null;
  currentC: number | null;
  currentN: number | null;
  voltageAn: number | null;
  voltageBn: number | null;
  voltageCn: number | null;
  activePowerA: number | null;
  activePowerB: number | null;
  activePowerC: number | null;
  activePowerTotal: number | null;
  powerFactorA: number | null;
  powerFactorB: number | null;
  powerFactorC: number | null;
  powerFactorTotal: number | null;
}

export interface PowerTag {
  topic: string;
  metadata: PowerTagMetadata;
  values: PowerTagValues;
}

export interface PowerTagPanel {
  id: string;
  powerTags: PowerTag[];
}

export type PowerTagsQueryResponse = { powerTags: PowerTag[] };

export type PowerTagPanelsQueryResponse = { powerTagPanels: PowerTagPanel[] };

export type PowerTagPanelQueryResponse = { powerTagPanel: PowerTagPanel | null };
