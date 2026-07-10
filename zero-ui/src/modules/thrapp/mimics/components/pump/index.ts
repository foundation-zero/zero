import { ComponentOrientation, MimicComponentState } from "..";

export const FIGMA_URL =
  "https://www.figma.com/design/DDNAUHsV56fQMTh3Ej76gL/App-screens---On-board-monitoring?node-id=6124-32160&t=JfBIEDjiEP5NKk6I-4";

export const enum PumpState {
  Active = "active",
  Inactive = "inactive",
}

export interface PumpProps {
  pumpState?: PumpState | MimicComponentState;
}

interface PumpStateColors {
  body: string;
  ring: string;
  blade: string;
}

export const PUMP_WIDTH = 54;
export const PUMP_HEIGHT = 54;
export const PUMP_RADIUS = 20.25;
export const PUMP_CENTER_X = PUMP_WIDTH / 2;
export const PUMP_CENTER_Y = PUMP_HEIGHT / 2;
export const PUMP_BASE_ORIENTATION = ComponentOrientation.Right;

export const PUMP_STATE_COLORS: Record<PumpState | MimicComponentState, PumpStateColors> = {
  [PumpState.Active]: {
    body: "var(--background)",
    ring: "var(--attention)",
    blade: "var(--constructive-muted)",
  },
  [PumpState.Inactive]: {
    body: "var(--background)",
    ring: "var(--attention)",
    blade: "var(--destructive-dull)",
  },
  [MimicComponentState.Alarm]: {
    body: "var(--destructive-dull)",
    ring: "var(--destructive)",
    blade: "var(--destructive-muted)",
  },
  [MimicComponentState.Manual]: {
    body: "var(--warning-muted)",
    ring: "var(--warning)",
    blade: "var(--warning)",
  },
  [MimicComponentState.Normal]: {
    body: "var(--background)",
    ring: "var(--attention)",
    blade: "var(--constructive-muted)",
  },
};
