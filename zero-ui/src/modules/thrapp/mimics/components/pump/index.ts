import { ComponentOrientation } from "..";

export const FIGMA_URL =
  "https://www.figma.com/design/DDNAUHsV56fQMTh3Ej76gL/App-screens---On-board-monitoring?node-id=6124-32160&t=JfBIEDjiEP5NKk6I-4";

export const enum PumpState {
  Active = "active",
  Transient = "transient",
  Closed = "closed",
  Alarm = "alarm",
}

export interface PumpProps {
  state?: PumpState;
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

export const PUMP_STATE_COLORS: Record<PumpState, PumpStateColors> = {
  [PumpState.Active]: {
    body: "var(--background)",
    ring: "var(--attention)",
    blade: "var(--constructive-muted)",
  },
  [PumpState.Transient]: {
    body: "var(--background)",
    ring: "var(--attention)",
    blade: "var(--warning)",
  },
  [PumpState.Closed]: {
    body: "var(--background)",
    ring: "var(--attention)",
    blade: "var(--destructive-dull)",
  },
  [PumpState.Alarm]: {
    body: "var(--destructive-dull)",
    ring: "var(--destructive)",
    blade: "var(--destructive-muted)",
  },
};
