import { ComponentOrientation, HeatingState } from "..";

export const FIGMA_URL =
  "https://www.figma.com/design/DDNAUHsV56fQMTh3Ej76gL/App-screens---On-board-monitoring?node-id=6799-68013&t=JfBIEDjiEP5NKk6I-4";

export const enum HeatExchangerPortOrientation {
  Side = "side",
  Top = "top",
}

export interface HeatExchangerProps {
  state?: HeatingState;
}

export interface HeatExchangerPortProps {
  state: HeatingState;
  orientation: HeatExchangerPortOrientation;
  side: "a" | "b";
}

export const HEAT_EXCHANGER_WIDTH = 56;
export const HEAT_EXCHANGER_HEIGHT = 56;
export const HEAT_EXCHANGER_BASE_ORIENTATION = ComponentOrientation.Right;

export const HEAT_EXCHANGER_SHELL = {
  x: 5,
  y: 5,
  width: 46,
  height: 46,
};

export const HEAT_EXCHANGER_PORT_CONNECTOR_R = 4;

export const HEAT_EXCHANGER_PORT_CONNECTORS: Record<
  HeatExchangerPortOrientation,
  Array<{ cx: number; cy: number }>
> = {
  [HeatExchangerPortOrientation.Side]: [
    { cx: 12, cy: 5 },
    { cx: 12, cy: 51 },
  ],
  [HeatExchangerPortOrientation.Top]: [
    { cx: 5, cy: 12 },
    { cx: 5, cy: 44 },
  ],
};

export const HEAT_EXCHANGER_PORT_PATHS: Record<HeatExchangerPortOrientation, string> = {
  [HeatExchangerPortOrientation.Side]:
    "M12 5 L12 12 H26L16 16L26 20L16 24L26 28L16 32L26 36L16 40L26 44H12 L12 51",
  [HeatExchangerPortOrientation.Top]: "M4 12 H26L16 16L26 20L16 24L26 28L16 32L26 36L16 40L26 44H4",
};
