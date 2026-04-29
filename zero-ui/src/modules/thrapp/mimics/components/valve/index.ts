import { ComponentOrientation } from "..";

export const FIGMA_URL = [
  "https://www.figma.com/design/DDNAUHsV56fQMTh3Ej76gL/App-screens---On-board-monitoring?node-id=6147-49293&t=F5BbOnx3UPamIB2S-4",
  "https://www.figma.com/design/DDNAUHsV56fQMTh3Ej76gL/App-screens---On-board-monitoring?node-id=6147-49298&t=F5BbOnx3UPamIB2S-4",
  "https://www.figma.com/design/DDNAUHsV56fQMTh3Ej76gL/App-screens---On-board-monitoring?node-id=6147-49304&t=F5BbOnx3UPamIB2S-4",
];

export const enum FlowValveState {
  Open = "open",
  Partial = "partial",
  Closed = "closed",
}

export const enum SwitchValveState {
  Open = "open",
  Closed = "closed",
}

export const enum ThreeWayValveState {
  Open = "open",
  AA = "a-a",
  AB = "a-b",
  BA = "b-a",
  Closed = "closed",
}

export const enum ValveType {
  FlowControl = "flow-control",
  Switch = "switch",
  ThreeWay = "three-way",
}

export interface ValveProps<T extends ValveType> {
  orientation?: ComponentOrientation;
  type: T;
}

export interface SwitchValveProps {
  state: SwitchValveState;
  markerLabel?: string;
}

export interface FlowValveProps {
  state: FlowValveState;
}

export interface ThreeWayValveProps {
  state: ThreeWayValveState;
}

export const enum ValvePort {
  Left = "left",
  Right = "right",
  Bottom = "bottom",
}

export const enum ValveColors {
  Open = "var(--constructive-dull)",
  Partial = "var(--warning-dull)",
  Closed = "var(--destructive-dull)",
}

export type ValvePortColors = Partial<Record<ValvePort, ValveColors>>;

export const VALVE_PORT_COLORS: Record<
  SwitchValveState | FlowValveState | ThreeWayValveState,
  ValvePortColors
> = {
  [SwitchValveState.Open]: {
    [ValvePort.Left]: ValveColors.Open,
    [ValvePort.Right]: ValveColors.Open,
    [ValvePort.Bottom]: ValveColors.Open,
  },
  [SwitchValveState.Closed]: {
    [ValvePort.Left]: ValveColors.Closed,
    [ValvePort.Right]: ValveColors.Closed,
    [ValvePort.Bottom]: ValveColors.Closed,
  },
  [FlowValveState.Partial]: {
    [ValvePort.Left]: ValveColors.Partial,
    [ValvePort.Right]: ValveColors.Partial,
  },
  [ThreeWayValveState.AA]: {
    [ValvePort.Left]: ValveColors.Open,
    [ValvePort.Right]: ValveColors.Open,
    [ValvePort.Bottom]: ValveColors.Closed,
  },
  [ThreeWayValveState.AB]: {
    [ValvePort.Left]: ValveColors.Open,
    [ValvePort.Right]: ValveColors.Closed,
    [ValvePort.Bottom]: ValveColors.Open,
  },
  [ThreeWayValveState.BA]: {
    [ValvePort.Left]: ValveColors.Closed,
    [ValvePort.Right]: ValveColors.Open,
    [ValvePort.Bottom]: ValveColors.Open,
  },
};

export const VALVE_WIDTH = 36;
export const VALVE_HEIGHT = 36;
export const VALVE_STROKE_COLOR = "var(--attention)";
export const VALVE_MARKER_COLOR = "var(--inverse-muted)";
export const VALVE_MARKER_TEXT_COLOR = "var(--inverse-foreground)";
export const VALVE_BASE_ORIENTATION = ComponentOrientation.Up;
