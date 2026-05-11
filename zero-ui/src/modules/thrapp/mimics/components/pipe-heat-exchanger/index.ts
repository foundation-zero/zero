import { ComponentOrientation } from "..";

export enum PipeHeatExchangerState {
  Idle = "Idle",
  Heating = "Heating",
  Cooling = "Cooling",
}

export interface PipeHeatExchangerProps {
  state?: PipeHeatExchangerState;
}

export const FIGMA_URL =
  "https://www.figma.com/design/DDNAUHsV56fQMTh3Ej76gL/App-screens---On-board-monitoring?node-id=5020-43327&t=JfBIEDjiEP5NKk6I-4";

export const PIPE_HEAT_EXCHANGER_WIDTH = 52;
export const PIPE_HEAT_EXCHANGER_HEIGHT = 52;
export const PIPE_HEAT_EXCHANGER_BASE_ORIENTATION = ComponentOrientation.Right;

export const PIPE_HEAT_EXCHANGER_FILL_COLORS: Record<PipeHeatExchangerState, string> = {
  [PipeHeatExchangerState.Idle]: "var(--background)",
  [PipeHeatExchangerState.Heating]: "var(--heating-medium)",
  [PipeHeatExchangerState.Cooling]: "var(--cooling-medium)",
};

export const PIPE_HEAT_EXCHANGER_INNER_FILL_COLORS: Record<PipeHeatExchangerState, string> = {
  [PipeHeatExchangerState.Idle]: "none",
  [PipeHeatExchangerState.Heating]: "var(--heating-high)",
  [PipeHeatExchangerState.Cooling]: "var(--cooling-high)",
};
