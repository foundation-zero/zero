import { NumberFormatter } from "@/modules/common/lib/utils.ts";
import { HTMLAttributes } from "vue";
import Auto from "./AutoRenderer.vue";
import BoilerTankControllerMode from "./BoilerTankControllerModeRenderer.vue";
import BoilerTankMode from "./BoilerTankModeRenderer.vue";
import DeltaT from "./DeltaTRenderer.vue";
import EnabledDisabled from "./EnabledDisabledRenderer.vue";
import Energy from "./EnergyRenderer.vue";
import FlowRate from "./FlowRateRenderer.vue";
import Frequency from "./FrequencyRenderer.vue";
import HeatExchangerMode from "./HeatExchangerModeRenderer.vue";
import HeatPumpMode from "./HeatPumpModeRenderer.vue";
import Heat from "./HeatRenderer.vue";
import Level from "./LevelRenderer.vue";
import Number from "./NumberRenderer.vue";
import OnOff from "./OnOffRenderer.vue";
import Percentage from "./PercentageRenderer.vue";
import PositionAbsolute from "./PositionAbsoluteRenderer.vue";
import Power from "./PowerRenderer.vue";
import Pressure from "./PressureRenderer.vue";
import QuantityLiters from "./QuantityLitersRenderer.vue";
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
  BoilerTankControllerMode,
  ValveState,
  Percentage,
  FlowRate,
  PositionAbsolute,
  Level,
  TimeRemaining,
  Source,
  DeltaT,
  Heat,
  HeatExchangerMode,
  OnOff,
  Pressure,
  Energy,
  Power,
  Frequency,
  QuantityLiters,
  Auto,
  EnabledDisabled,
};
