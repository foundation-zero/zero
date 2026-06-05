import { ComponentOrientation } from "..";

export const FIGMA_URL = [
  "https://www.figma.com/design/DDNAUHsV56fQMTh3Ej76gL/App-screens---On-board-monitoring?node-id=6147-49293&t=F5BbOnx3UPamIB2S-4",
  "https://www.figma.com/design/DDNAUHsV56fQMTh3Ej76gL/App-screens---On-board-monitoring?node-id=6147-49298&t=F5BbOnx3UPamIB2S-4",
  "https://www.figma.com/design/DDNAUHsV56fQMTh3Ej76gL/App-screens---On-board-monitoring?node-id=6147-49304&t=F5BbOnx3UPamIB2S-4",
];

export const enum ActuatedValvePort {
  Left = "left",
  Right = "right",
  Bottom = "bottom",
}

export const enum ActuatedValveColors {
  Open = "var(--constructive-dull)",
  Partial = "var(--warning-dull)",
  Closed = "var(--destructive-dull)",
}

export type PortProps = {
  d: string;
  flow: number;
};

export const ACTUATED_VALVE_WIDTH = 36;
export const ACTUATED_VALVE_HEIGHT = 36;
export const ACTUATED_VALVE_STROKE_COLOR = "var(--attention)";
export const ACTUATED_VALVE_MARKER_COLOR = "var(--muted)";
export const ACTUATED_VALVE_MARKER_TEXT_COLOR = "var(--foreground)";
export const ACTUATED_VALVE_BASE_ORIENTATION = ComponentOrientation.Up;
