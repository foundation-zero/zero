import { Component } from "vue";
import { MimicComponentType } from "../../types/index.ts";
import BoilerTankTooltip from "./BoilerTankTooltip.vue";

export { default as BoilerTankTooltip } from "./BoilerTankTooltip.vue";

export const TOOLTIPS: Partial<Record<MimicComponentType, Component>> = {
  [MimicComponentType.BoilerTank]: BoilerTankTooltip,
};
