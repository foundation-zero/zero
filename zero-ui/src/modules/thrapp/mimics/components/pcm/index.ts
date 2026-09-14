import { MimicComponentState } from "..";

export { default as Pcm } from "./Pcm.vue";
export { default as PcmChargeState } from "./PcmChargeState.vue";
export { default as PcmChargingMode } from "./PcmChargingMode.vue";
export { default as PcmTitle } from "./PcmTitle.vue";

export const REM = 16;
export const PCM_WIDTH = 260;
export const PCM_HEIGHT = 180;
export const HEAT_PIPES_TOP_LEFT_POSITION = {
  x: 0.06269 * REM,
  y: 1.418 * REM,
};
export const HEAT_PIPES_BOTTOM_LEFT_POSITION = {
  x: 0.06269 * REM,
  y: 6.84 * REM,
};
export const HEAT_PIPES_BOTTOM_RIGHT_POSITION = {
  x: 13.7 * REM,
  y: 6.8 * REM,
};
export const PCM_TITLE_LEFT = 50;
export const PCM_CONTENT_LEFT = 50;
export const PCM_CONTENT_RIGHT_WITH_PORTS = 0;
export const PCM_CONTENT_RIGHT_DIAGONAL = 32;
export const FIGMA_URL =
  "https://www.figma.com/design/DDNAUHsV56fQMTh3Ej76gL/App-screens---On-board-monitoring?node-id=8986-190520&m=dev";

export const enum PcmLayout {
  LeftTopBottom = "left-top-bottom",
  LeftRight = "left-right",
}

export const enum ChargingMode {
  Charging = "charging",
  Discharging = "discharging",
  Idle = "idle",
}

export const enum ChargeState {
  Full = "full",
  Empty = "empty",
  HalfFull = "half-full",
}

export const CHARGING_MODE_COLORS: Record<ChargingMode, string> = {
  [ChargingMode.Charging]: "var(--constructive)",
  [ChargingMode.Discharging]: "var(--flows-use-medium)",
  [ChargingMode.Idle]: "var(--muted-foreground)",
};

export const CHARGE_STATE_COLORS: Record<ChargeState, string> = {
  [ChargeState.Full]: "var(--flows-heat-high)",
  [ChargeState.Empty]: "var(--flows-heat-low)",
  [ChargeState.HalfFull]: "var(--flows-heat-medium)",
};

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
