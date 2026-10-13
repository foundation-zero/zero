import { NumberFormatter } from "@/modules/common/lib/utils.ts";
import { HTMLAttributes } from "vue";
import Auto from "./AutoRenderer.vue";
import BoilerTankControllerMode from "./BoilerTankControllerModeRenderer.vue";
import BoilerTankMode from "./BoilerTankModeRenderer.vue";
import BoilerTankTemperature from "./BoilerTankTemperatureRenderer.vue";
import ChargeState from "./ChargeStateRenderer.vue";
import ChargingMode from "./ChargingModeRenderer.vue";
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
import ThreeWayValveState from "./ThreeWayValveStateRenderer.vue";
import TimeRemaining from "./TimeRemainingRenderer.vue";
import ValveState from "./ValveStateRenderer.vue";

export type FieldRendererProps<T> = {
  value?: T;
  class?: HTMLAttributes["class"];
  format?: NumberFormatter;
  transform?: (value: T) => T;
};

export const FieldRenderer = {
  get Placeholder() {
    return Placeholder;
  },
  get Number() {
    return Number;
  },
  get Temperature() {
    return Temperature;
  },
  get HeatPumpMode() {
    return HeatPumpMode;
  },
  get BoilerTankMode() {
    return BoilerTankMode;
  },
  get BoilerTankTemperature() {
    return BoilerTankTemperature;
  },
  get BoilerTankControllerMode() {
    return BoilerTankControllerMode;
  },
  get ValveState() {
    return ValveState;
  },
  get ThreeWayValveState() {
    return ThreeWayValveState;
  },
  get Percentage() {
    return Percentage;
  },
  get FlowRate() {
    return FlowRate;
  },
  get Degree() {
    return Degree;
  },
  get Level() {
    return Level;
  },
  get TimeRemaining() {
    return TimeRemaining;
  },
  get Source() {
    return Source;
  },
  get DeltaT() {
    return DeltaT;
  },
  get Heat() {
    return Heat;
  },
  get HeatExchangerMode() {
    return HeatExchangerMode;
  },
  get OnOff() {
    return OnOff;
  },
  get Pressure() {
    return Pressure;
  },
  get Energy() {
    return Energy;
  },
  get Power() {
    return Power;
  },
  get Frequency() {
    return Frequency;
  },
  get QuantityLiters() {
    return QuantityLiters;
  },
  get Auto() {
    return Auto;
  },
  get EnabledDisabled() {
    return EnabledDisabled;
  },
  get Empty() {
    return Empty;
  },
  get PvtMode() {
    return PvtMode;
  },
  get Irradiance() {
    return Irradiance;
  },
  get ChargeState() {
    return ChargeState;
  },
  get ChargingMode() {
    return ChargingMode;
  },
};
