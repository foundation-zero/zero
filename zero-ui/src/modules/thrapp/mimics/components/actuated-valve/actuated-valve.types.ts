import { ValveLeg, ValvePortName } from "./actuated-valve.consts";

export type PortProps = {
  d: string;
  flow: number;
};

export type ValveLegLabelProps = {
  x: number;
  y: number;
  width: number;
};

/**
 * Which port sits on which leg. Configurable per instance because the schematic
 * dictates the layout; it is fixed up front and never derived from flow.
 */
export type ThreeWayValveLegs = Record<ValveLeg, ValvePortName>;
