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

export const enum ActuatedValveType {
  FlowControl = "flow-control",
  Switch = "switch",
  ThreeWay = "three-way",
}

export interface ActuatedValveProps<T extends ActuatedValveType> {
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

export type ActuatedValvePortColors = Partial<Record<ActuatedValvePort, ActuatedValveColors>>;

export const ACTUATED_VALVE_PORT_COLORS: Record<
  SwitchValveState | FlowValveState | ThreeWayValveState,
  ActuatedValvePortColors
> = {
  [SwitchValveState.Open]: {
    [ActuatedValvePort.Left]: ActuatedValveColors.Open,
    [ActuatedValvePort.Right]: ActuatedValveColors.Open,
    [ActuatedValvePort.Bottom]: ActuatedValveColors.Open,
  },
  [SwitchValveState.Closed]: {
    [ActuatedValvePort.Left]: ActuatedValveColors.Closed,
    [ActuatedValvePort.Right]: ActuatedValveColors.Closed,
    [ActuatedValvePort.Bottom]: ActuatedValveColors.Closed,
  },
  [FlowValveState.Partial]: {
    [ActuatedValvePort.Left]: ActuatedValveColors.Partial,
    [ActuatedValvePort.Right]: ActuatedValveColors.Partial,
  },
  [ThreeWayValveState.AA]: {
    [ActuatedValvePort.Left]: ActuatedValveColors.Open,
    [ActuatedValvePort.Right]: ActuatedValveColors.Open,
    [ActuatedValvePort.Bottom]: ActuatedValveColors.Closed,
  },
  [ThreeWayValveState.AB]: {
    [ActuatedValvePort.Left]: ActuatedValveColors.Open,
    [ActuatedValvePort.Right]: ActuatedValveColors.Closed,
    [ActuatedValvePort.Bottom]: ActuatedValveColors.Open,
  },
  [ThreeWayValveState.BA]: {
    [ActuatedValvePort.Left]: ActuatedValveColors.Closed,
    [ActuatedValvePort.Right]: ActuatedValveColors.Open,
    [ActuatedValvePort.Bottom]: ActuatedValveColors.Open,
  },
};

export const ACTUATED_VALVE_WIDTH = 36;
export const ACTUATED_VALVE_HEIGHT = 36;
export const ACTUATED_VALVE_STROKE_COLOR = "var(--attention)";
export const ACTUATED_VALVE_MARKER_COLOR = "var(--inverse-muted)";
export const ACTUATED_VALVE_MARKER_TEXT_COLOR = "var(--inverse-foreground)";
export const ACTUATED_VALVE_BASE_ORIENTATION = ComponentOrientation.Up;
