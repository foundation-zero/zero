import { ComponentOrientation } from "..";

export const FIGMA_URL = [
  "https://www.figma.com/design/DDNAUHsV56fQMTh3Ej76gL/App-screens---On-board-monitoring?node-id=6186-116693",
  "https://www.figma.com/design/DDNAUHsV56fQMTh3Ej76gL/App-screens---On-board-monitoring?node-id=6186-116697",
  "https://www.figma.com/design/DDNAUHsV56fQMTh3Ej76gL/App-screens---On-board-monitoring?node-id=6186-116701",
];

export const enum ManualValveType {
  Switch = "switch",
  FlowControl = "flow-control",
  ThreeWay = "three-way",
}

export interface ManualValveProps {
  type: ManualValveType;
}

export const MANUAL_VALVE_WIDTH = 36;
export const MANUAL_VALVE_HEIGHT = 36;
export const MANUAL_VALVE_PORT_FILL = "var(--background)";
export const MANUAL_VALVE_BORDER_COLOR = "var(--brand-muted)";
export const MANUAL_VALVE_PIVOT_BORDER_COLOR = "var(--inverse-border-subtle)";
export const MANUAL_VALVE_MARK_COLOR = "var(--foreground)";
export const MANUAL_VALVE_BASE_ORIENTATION = ComponentOrientation.Up;
