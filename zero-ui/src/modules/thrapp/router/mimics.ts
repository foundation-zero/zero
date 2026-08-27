import { ThrsModules } from "@/modules/thrsim/lib/consts";
import { Component, defineAsyncComponent } from "vue";
import { MimicComponentFieldsMap } from "../mimics/modules";
import { DHW_MIMIC_DATA } from "../mimics/modules/dhw/data";
import { THRUSTERS_MIMIC_DATA } from "../mimics/modules/thrusters/data";

export type MimicDefinition = {
  component: Component;
  legend?: Component;
  data: Partial<MimicComponentFieldsMap>;
};

export const MIMICS: Partial<Record<keyof ThrsModules, MimicDefinition>> = {
  dhw: {
    component: defineAsyncComponent(
      () => import("@/modules/thrapp/mimics/modules/dhw/DhwModule.vue"),
    ),
    legend: defineAsyncComponent(
      () => import("@/modules/thrapp/components/legends/BoilerLegend.vue"),
    ),
    data: DHW_MIMIC_DATA,
  },
  thrusters: {
    component: defineAsyncComponent(
      () => import("@/modules/thrapp/mimics/modules/thrusters/ThrustersModule.vue"),
    ),
    data: THRUSTERS_MIMIC_DATA,
  },
};
