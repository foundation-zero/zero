import { MimicComponentState } from "..";
import { PumpState } from "./pump.consts";

export interface PumpProps {
  pumpState?: PumpState | MimicComponentState;
  manual?: boolean;
  width?: number;
  height?: number;
}

export interface PumpStateColors {
  body: string;
  ring: string;
  blade: string;
}
