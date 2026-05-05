import { ComponentOrientation } from "..";

export const FIGMA_URL =
  "https://www.figma.com/design/DDNAUHsV56fQMTh3Ej76gL/App-screens---On-board-monitoring?node-id=6147-47124&t=JfBIEDjiEP5NKk6I-4";

export const enum HeatExchangerState {
  HeatAB = "heat-a-b",
  HeataB = "heat-a-B",
  CoolAB = "cool-a-b",
  CoolaB = "cool-a-B",
  Idle = "idle",
}

export interface HeatExchangerProps {
  state?: HeatExchangerState;
  orientation?: ComponentOrientation;
}

interface HeatExchangerStateColors {
  shell: string;
  exchangerLeft: string;
  exchangerRight: string;
}

export const HEAT_EXCHANGER_WIDTH = 36;
export const HEAT_EXCHANGER_HEIGHT = 36;
export const HEAT_EXCHANGER_BASE_ORIENTATION = ComponentOrientation.Right;

export const HEAT_EXCHANGER_SHELL = {
  x: 6.5,
  y: 6.5,
  width: 23,
  height: 23,
};

export const HEAT_EXCHANGER_STATE_COLORS: Record<HeatExchangerState, HeatExchangerStateColors> = {
  [HeatExchangerState.HeatAB]: {
    shell: "var(--attention)",
    exchangerLeft: "var(--heating-medium)",
    exchangerRight: "var(--heating-low)",
  },
  [HeatExchangerState.HeataB]: {
    shell: "var(--attention)",
    exchangerLeft: "var(--cooling-medium)",
    exchangerRight: "var(--cooling-medium)",
  },
  [HeatExchangerState.CoolAB]: {
    shell: "transparent",
    exchangerLeft: "var(--cooling-medium)",
    exchangerRight: "var(--cooling-low)",
  },
  [HeatExchangerState.CoolaB]: {
    shell: "var(--attention)",
    exchangerLeft: "var(--cooling-low)",
    exchangerRight: "var(--cooling-medium)",
  },
  [HeatExchangerState.Idle]: {
    shell: "var(--attention-dull)",
    exchangerLeft: "var(--disabled-foreground)",
    exchangerRight: "var(--disabled-foreground)",
  },
};
