import { DcMode, SensorComponentType } from "@/modules/thrsim/types";
import { ModuleField } from "../../providers";
import { ModeBadgeMode } from "../mode-badge";
export { default as DcConverterStatus } from "./DcConverterStatus.vue";
export { default as DcMode } from "./DcMode.vue";

export const DC_CONVERTER_WIDTH = 200;
export const DC_CONVERTER_HEIGHT = 205;

export const DC_MODE_COLORS: Record<DcMode, ModeBadgeMode> = {
  [DcMode.Recovery]: ModeBadgeMode.Active,
  [DcMode.Idle]: ModeBadgeMode.Idle,
};

export type DcConverterStatusProps = {
  sources: ModuleField<
    | SensorComponentType.Brightloop
    | SensorComponentType.Ugrid
    | SensorComponentType.ShorePowerConverter
  >[];
};

export type DcConverterTitleKey = "group1" | "group2" | "group3";
