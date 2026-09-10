import { NumberFormatter } from "@/modules/common/lib/utils.ts";
import { HTMLAttributes } from "vue";
import Auto from "./AutoRenderer.vue";
import BoilerTankControllerMode from "./BoilerTankControllerModeRenderer.vue";
import BoilerTankMode from "./BoilerTankModeRenderer.vue";
import Degree from "./DegreeRenderer.vue";
import DeltaT from "./DeltaTRenderer.vue";
import Empty from "./EmptyRenderer.vue";
import EnabledDisabled from "./EnabledDisabledRenderer.vue";
import Energy from "./EnergyRenderer.vue";
import FlowRate from "./FlowRateRenderer.vue";
import Frequency from "./FrequencyRenderer.vue";
import HeatExchangerMode from "./HeatExchangerModeRenderer.vue";
import HeatPumpMode from "./HeatPumpModeRenderer.vue";
import Heat from "./HeatRenderer.vue";
import Irradiance from "./IrradianceRenderer.vue";
import Level from "./LevelRenderer.vue";
import Number from "./NumberRenderer.vue";
import OnOff from "./OnOffRenderer.vue";
import Percentage from "./PercentageRenderer.vue";
import Placeholder from "./PlaceholderRenderer.vue";
import Power from "./PowerRenderer.vue";
import Pressure from "./PressureRenderer.vue";
import PvtMode from "./PvtModeRenderer.vue";
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
  Placeholder,
  Number,
  Temperature,
  HeatPumpMode,
  BoilerTankMode,
  BoilerTankControllerMode,
  ValveState,
  Percentage,
  FlowRate,
  Degree,
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
  Empty,
  PvtMode,
  Irradiance,
};
