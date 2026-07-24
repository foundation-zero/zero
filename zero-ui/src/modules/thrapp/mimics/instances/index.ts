import { MimicComponentBaseProps } from "../components";

export { default as CheckValveInstance } from "./CheckValveInstance.vue";
export { default as DutypointLabelInstance } from "./DutypointLabelInstance.vue";
export { default as FlowControlValveInstance } from "./FlowControlValveInstance.vue";
export { default as FlowSensorInstance } from "./FlowSensorInstance.vue";
export { default as HeatExchangerInstance } from "./HeatExchangerInstance.vue";
export { default as HeatExchangerLabelInstance } from "./HeatExchangerLabelInstance.vue";
export { default as LevelLabelInstance } from "./LevelLabelInstance.vue";
export { default as LevelSensorInstance } from "./LevelSensorInstance.vue";
export { default as LevelSwitchInstance } from "./LevelSwitchInstance.vue";
export { default as LoopCircuitInstance } from "./LoopCircuitInstance.vue";
export { default as ManualValveInstance } from "./ManualValveInstance.vue";
export { default as MixValveInstance } from "./MixValveInstance.vue";
export { default as PipeHeatExchangerInstance } from "./PipeHeatExchangerInstance.vue";
export { default as PressureGaugeInstance } from "./PressureGaugeInstance.vue";
export { default as PressureLabelInstance } from "./PressureLabelInstance.vue";
export { default as PressureSensorInstance } from "./PressureSensorInstance.vue";
export { default as PumpInstance } from "./PumpInstance.vue";
export { default as SwitchValveInstance } from "./SwitchValveInstance.vue";
export { default as TagLabelInstance } from "./TagLabelInstance.vue";
export { default as TemperatureSensorInstance } from "./TemperatureSensorInstance.vue";
export { default as ThreeWaySwitchValveInstance } from "./ThreeWaySwitchValveInstance.vue";
export { default as ThreeWayValveLabelInstance } from "./ThreeWayValveLabelInstance.vue";

export type TitleProps = {
  title: string;
};
export type MimicComponentInstanceProps = MimicComponentBaseProps & {
  x?: number | string;
  y?: number | string;
  tagId?: string;
};
