import { tScoped } from "@/modules/common/lib/utils.ts";
import { Component, defineAsyncComponent } from "vue";
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
  [MimicComponentType.ManualValve]: defineAsyncComponent(() => import("./ManualValveTooltip.vue")),
  [MimicComponentType.PressureSensor]: defineAsyncComponent(
    () => import("./PressureSensorTooltip.vue"),
  ),
  [MimicComponentType.FlowSensor]: defineAsyncComponent(() => import("./FlowSensorTooltip.vue")),
  [MimicComponentType.TemperatureSensor]: defineAsyncComponent(
    () => import("./TemperatureSensorTooltip.vue"),
  ),
  [MimicComponentType.Asset]: defineAsyncComponent(() => import("./AssetTooltip.vue")),
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
});
