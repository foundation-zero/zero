import { Ratio } from "@/modules/thrapp/types/thrs";
import {
  VALVE_CENTER,
  VALVE_LEG_LABEL_HEIGHT,
  VALVE_LEG_LABEL_INSETS,
  VALVE_LEG_LABEL_WIDTHS,
  ValveLeg,
  ValvePortName,
} from "./actuated-valve.consts";
import { ThreeWayValveLegs, ValveLegLabelProps } from "./actuated-valve.types";

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
