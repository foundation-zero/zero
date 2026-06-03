import { MimicComponentBaseProps } from "../components";

export { default as ActuatedValveInstance } from "./ActuatedValveInstance.vue";
export { default as CheckValveInstance } from "./CheckValveInstance.vue";
export { default as FlowSensorInstance } from "./FlowSensorInstance.vue";
export { default as HeatExchangerInstance } from "./HeatExchangerInstance.vue";
export { default as HeatExchangerLabelInstance } from "./HeatExchangerLabelInstance.vue";
export { default as LevelSensorInstance } from "./LevelSensorInstance.vue";
export { default as LoopCircuitInstance } from "./LoopCircuitInstance.vue";
export { default as ManualValveInstance } from "./ManualValveInstance.vue";
export { default as PipeHeatExchangerInstance } from "./PipeHeatExchangerInstance.vue";
export { default as PressureGaugeInstance } from "./PressureGaugeInstance.vue";
export { default as PressureSensorInstance } from "./PressureSensorInstance.vue";
export { default as PumpInstance } from "./PumpInstance.vue";
export { default as TemperatureSensorInstance } from "./TemperatureSensorInstance.vue";

export type TitleProps = {
  title: string;
};
export type MimicComponentInstanceProps = MimicComponentBaseProps & {
  x?: number | string;
  y?: number | string;
  tagId?: string;
};
