import { Component, defineAsyncComponent } from "vue";
import { MimicComponentType } from "../../types";

export const TOOLTIPS: Partial<Record<MimicComponentType, Component>> = {
  [MimicComponentType.ExpansionValve]: defineAsyncComponent(
    () => import("./ExpansionValveTooltip.vue"),
  ),
  [MimicComponentType.ExpansionTank]: defineAsyncComponent(
    () => import("./ExpansionTankTooltip.vue"),
  ),
  [MimicComponentType.Pyranometer]: defineAsyncComponent(() => import("./PyranometerTooltip.vue")),
  [MimicComponentType.AirTrapVessel]: defineAsyncComponent(
    () => import("./AirTrapVesselTooltip.vue"),
  ),
  [MimicComponentType.BoilerTank]: defineAsyncComponent(() => import("./BoilerTankTooltip.vue")),
  [MimicComponentType.SwitchValve]: defineAsyncComponent(() => import("./SwitchValveTooltip.vue")),
  [MimicComponentType.FlowControlValve]: defineAsyncComponent(
    () => import("./FlowControlValveTooltip.vue"),
  ),
  [MimicComponentType.HeatExchanger]: defineAsyncComponent(
    () => import("./HeatExchangerTooltip.vue"),
  ),
  [MimicComponentType.Pump]: defineAsyncComponent(() => import("./PumpTooltip.vue")),
  [MimicComponentType.ManualPump]: defineAsyncComponent(() => import("./ManualPumpTooltip.vue")),
  [MimicComponentType.ManualValve]: defineAsyncComponent(() => import("./ManualValveTooltip.vue")),
  [MimicComponentType.PressureSensor]: defineAsyncComponent(
    () => import("./PressureSensorTooltip.vue"),
  ),
  [MimicComponentType.PressureGauge]: defineAsyncComponent(
    () => import("./PressureGaugeTooltip.vue"),
  ),
  [MimicComponentType.MixValve]: defineAsyncComponent(() => import("./MixValveTooltip.vue")),
  [MimicComponentType.CheckValve]: defineAsyncComponent(() => import("./CheckValveTooltip.vue")),
  [MimicComponentType.ThreeWaySwitchValve]: defineAsyncComponent(
    () => import("./ThreeWaySwitchValveTooltip.vue"),
  ),
  [MimicComponentType.FlowSensor]: defineAsyncComponent(() => import("./FlowSensorTooltip.vue")),
  [MimicComponentType.LevelSensor]: defineAsyncComponent(() => import("./LevelSensorTooltip.vue")),
  [MimicComponentType.LevelSwitch]: defineAsyncComponent(() => import("./LevelSwitchTooltip.vue")),
  [MimicComponentType.TemperatureSensor]: defineAsyncComponent(
    () => import("./TemperatureSensorTooltip.vue"),
  ),
  [MimicComponentType.HVAC]: defineAsyncComponent(() => import("./HVACTooltip.vue")),
  [MimicComponentType.HeatPump]: defineAsyncComponent(() => import("./HeatPumpTooltip.vue")),
  [MimicComponentType.ConnectingCircuit]: defineAsyncComponent(
    () => import("./ConnectingCircuitTooltip.vue"),
  ),
  [MimicComponentType.FreshwaterCircuit]: defineAsyncComponent(
    () => import("./FreshwaterCircuitTooltip.vue"),
  ),
  [MimicComponentType.SeawaterCircuit]: defineAsyncComponent(
    () => import("./SeawaterCircuitTooltip.vue"),
  ),
  [MimicComponentType.ExchangeCircuit]: defineAsyncComponent(
    () => import("./ExchangeCircuitTooltip.vue"),
  ),
  [MimicComponentType.Pvt]: defineAsyncComponent(() => import("./PvtTooltip.vue")),
  [MimicComponentType.PvtString]: defineAsyncComponent(() => import("./PvtStringTooltip.vue")),
  [MimicComponentType.DcConverter]: defineAsyncComponent(() => import("./DcConverterTooltip.vue")),
  [MimicComponentType.Pcm]: defineAsyncComponent(() => import("./PcmTooltip.vue")),
  [MimicComponentType.Thruster]: defineAsyncComponent(() => import("./ThrustersTooltip.vue")),
  [MimicComponentType.PropulsionDrive]: defineAsyncComponent(
    () => import("./PropulsionDriveTooltip.vue"),
  ),
  [MimicComponentType.PropulsionCooler]: defineAsyncComponent(
    () => import("./PropulsionCoolerTooltip.vue"),
  ),
  [MimicComponentType.ShorePowerConverter]: defineAsyncComponent(
    () => import("./ShorePowerConverterTooltip.vue"),
  ),
};
