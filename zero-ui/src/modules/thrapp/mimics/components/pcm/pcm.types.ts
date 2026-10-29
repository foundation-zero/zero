import { MimicComponentState } from "..";
import { ChargeState, ChargingMode, PcmLayout } from "./pcm.consts";

export interface PcmChargingModeProps {
  mode?: ChargingMode;
}

export interface PcmChargeStateProps {
  state?: ChargeState;
}

export interface PcmProps {
  layout?: PcmLayout;
  state?: MimicComponentState;
}
