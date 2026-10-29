import { HeatingState } from "..";
import { HeatExchangerPortOrientation } from "./heat-exchanger.consts";

export interface HeatExchangerProps {
  heatingState?: HeatingState.Active | HeatingState.Inactive;
}

export interface HeatExchangerPortProps {
  state: HeatingState;
  orientation: HeatExchangerPortOrientation;
  side: "a" | "b";
}
