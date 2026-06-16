import { tScoped } from "@/modules/common/lib/utils.ts";
import { Component, defineAsyncComponent } from "vue";
import { MimicComponentType } from "../../types/index.ts";

export { default as BoilerTankTooltip } from "./BoilerTankTooltip.vue";

export const TOOLTIPS: Partial<Record<MimicComponentType, Component>> = {
  [MimicComponentType.BoilerTank]: defineAsyncComponent(() => import("./BoilerTankTooltip.vue")),
  [MimicComponentType.SwitchValve]: defineAsyncComponent(() => import("./SwitchValveTooltip.vue")),
  [MimicComponentType.FlowControlValve]: defineAsyncComponent(
    () => import("./FlowControlValveTooltip.vue"),
  ),
  [MimicComponentType.HeatExchanger]: defineAsyncComponent(
    () => import("./HeatExchangerTooltip.vue"),
  ),
};

export const useTranslations = () => ({
  units: tScoped("units"),
  actions: tScoped("thrapp.tooltips.actions"),
  items: tScoped("thrapp.tooltips.items"),
  labels: tScoped("thrapp.tooltips.labels"),
  sources: tScoped("thrapp.tooltips.sources"),
});
