import { Ratio } from "@/modules/thrsim/types";
import { ComponentOrientation } from "..";

export const FIGMA_URL = [
  "https://www.figma.com/design/DDNAUHsV56fQMTh3Ej76gL/App-screens---On-board-monitoring?node-id=6147-49293&t=F5BbOnx3UPamIB2S-4",
  "https://www.figma.com/design/DDNAUHsV56fQMTh3Ej76gL/App-screens---On-board-monitoring?node-id=6147-49298&t=F5BbOnx3UPamIB2S-4",
  "https://www.figma.com/design/DDNAUHsV56fQMTh3Ej76gL/App-screens---On-board-monitoring?node-id=6147-49304&t=F5BbOnx3UPamIB2S-4",
  "https://www.figma.com/design/sJJva5wHcwY62tIBG4Jsd8/Web-app-Library?node-id=1765-370&t=pys0uAevHAvq3jZy-4",
];

export const enum ValveLeg {
  Left = "left",
  Right = "right",
  Bottom = "bottom",
}

export const VALVE_LEGS = [ValveLeg.Left, ValveLeg.Right, ValveLeg.Bottom] as const;

export const enum ValvePortName {
  A = "A",
  B = "B",
  AB = "AB",
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

export type ValveLegLabelProps = {
  x: number;
  y: number;
  width: number;
};

export const ACTUATED_VALVE_WIDTH = 36;
export const ACTUATED_VALVE_HEIGHT = 36;
export const ACTUATED_VALVE_STROKE_COLOR = "var(--attention)";
export const ACTUATED_VALVE_MARKER_COLOR = "var(--muted)";
export const ACTUATED_VALVE_MARKER_TEXT_COLOR = "var(--foreground)";
export const ACTUATED_VALVE_BASE_ORIENTATION = ComponentOrientation.Up;

export const VALVE_LEG_LABEL_FONT_SIZE = 6;
export const VALVE_LEG_LABEL_HEIGHT = 6;
export const VALVE_LEG_LABEL_BACKGROUND_COLOR = "var(--background)";

/** Text box widths measured in Figma (Inter 400 at 6px). */
const VALVE_LEG_LABEL_WIDTHS: Record<ValvePortName, number> = {
  [ValvePortName.A]: 5,
  [ValvePortName.B]: 4,
  [ValvePortName.AB]: 8,
};

/** Figma distance from the valve centre to the inner edge of the label box. */
const VALVE_LEG_LABEL_INSETS: Record<ValveLeg, number> = {
  [ValveLeg.Left]: 14.39,
  [ValveLeg.Right]: 16.01,
  [ValveLeg.Bottom]: 15.08,
};

const VALVE_CENTER = ACTUATED_VALVE_WIDTH / 2;

/**
 * Which port sits on which leg. Configurable per instance because the schematic
 * dictates the layout; it is fixed up front and never derived from flow.
 */
export type ThreeWayValveLegs = Record<ValveLeg, ValvePortName>;

export const THREE_WAY_VALVE_DEFAULT_LEGS: ThreeWayValveLegs = {
  [ValveLeg.Left]: ValvePortName.A,
  [ValveLeg.Right]: ValvePortName.AB,
  [ValveLeg.Bottom]: ValvePortName.B,
};

/** AB is the common port; A and B share what is left between them. */
export const createThreeWayValveFlows = (
  legs: ThreeWayValveLegs,
  flow: Ratio,
): Record<ValveLeg, number> => {
  const portFlows: Record<ValvePortName, number> = {
    [ValvePortName.A]: flow,
    [ValvePortName.B]: 1 - flow,
    [ValvePortName.AB]: 1,
  };

  return {
    [ValveLeg.Left]: portFlows[legs[ValveLeg.Left]],
    [ValveLeg.Right]: portFlows[legs[ValveLeg.Right]],
    [ValveLeg.Bottom]: portFlows[legs[ValveLeg.Bottom]],
  };
};

/**
 * Anchors the label box just past the leg tip, outside the 36x36 viewBox. The
 * outward size is the box height on the vertical leg and its width on the horizontal ones.
 */
export const createValveLegLabel = (leg: ValveLeg, port: ValvePortName): ValveLegLabelProps => {
  const width = VALVE_LEG_LABEL_WIDTHS[port];
  const outwardSize = leg === ValveLeg.Bottom ? VALVE_LEG_LABEL_HEIGHT : width;
  const offset = VALVE_LEG_LABEL_INSETS[leg] + outwardSize / 2;

  switch (leg) {
    case ValveLeg.Left:
      return { x: VALVE_CENTER - offset, y: VALVE_CENTER, width };
    case ValveLeg.Right:
      return { x: VALVE_CENTER + offset, y: VALVE_CENTER, width };
    case ValveLeg.Bottom:
      return { x: VALVE_CENTER, y: VALVE_CENTER + offset, width };
  }
};
