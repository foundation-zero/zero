import { NumberFormatter } from "@/modules/common/lib/utils.ts";
import { HTMLAttributes } from "vue";
import BoilerTankMode from "./BoilerTankModeRenderer.vue";
import FlowRate from "./FlowRateRenderer.vue";
import HeatPumpMode from "./HeatPumpModeRenderer.vue";
import Level from "./LevelRenderer.vue";
import Number from "./NumberRenderer.vue";
import Percentage from "./PercentageRenderer.vue";
import PositionAbsolute from "./PositionAbsoluteRenderer.vue";
import Source from "./SourceRenderer.vue";
import Temperature from "./TemperatureRenderer.vue";
import TimeRemaining from "./TimeRemainingRenderer.vue";
import ValveState from "./ValveStateRenderer.vue";

export type FieldRendererProps<T> = {
  value?: T;
  class?: HTMLAttributes["class"];
  format?: NumberFormatter;
};

export const FieldRenderer = {
  Number,
  Temperature,
  HeatPumpMode,
  BoilerTankMode,
  ValveState,
  Percentage,
  FlowRate,
  PositionAbsolute,
  Level,
  TimeRemaining,
  Source,
};
