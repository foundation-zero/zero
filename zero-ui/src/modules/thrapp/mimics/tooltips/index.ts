import { tScoped } from "@/modules/common/lib/utils.ts";
import { Component, defineAsyncComponent } from "vue";
import { useI18n } from "vue-i18n";
import { MimicComponentType } from "../../types/index.ts";

export const TOOLTIPS: Partial<Record<MimicComponentType, Component>> = {
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
  [MimicComponentType.HotWaterCircuit]: defineAsyncComponent(
    () => import("./HotWaterCircuitTooltip.vue"),
  ),
  [MimicComponentType.ExchangeCircuit]: defineAsyncComponent(
    () => import("./ExchangeCircuitTooltip.vue"),
  ),
};

export const useTranslations = () => ({
  units: tScoped("units"),
  actions: tScoped("thrapp.tooltips.actions"),
  items: tScoped("thrapp.tooltips.items"),
  labels: tScoped("thrapp.tooltips.labels"),
  sources: tScoped("thrapp.tooltips.sources"),
  t: useI18n().t,
});
