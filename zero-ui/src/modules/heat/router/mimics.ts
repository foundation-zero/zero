import { ThrsModules } from "@/modules/heat-simulation/lib/consts";
import { Component, defineAsyncComponent } from "vue";
import { MimicComponentFieldsMap } from "../mimics/modules";
import { DC_MIMIC_DATA } from "../mimics/modules/dc/data";
import { DHW_MIMIC_DATA } from "../mimics/modules/dhw/data";
import { DRIVES_MIMIC_DATA } from "../mimics/modules/drives/data";
import { PCM_MIMIC_DATA } from "../mimics/modules/pcm/data";
import { PVT_MIMIC_DATA } from "../mimics/modules/pvt/data";
import { THRUSTERS_MIMIC_DATA } from "../mimics/modules/thrusters/data";

export type MimicDefinition = {
  component: Component;
  legend?: Component;
  data: Partial<MimicComponentFieldsMap>;
};

export const MIMICS: Partial<Record<keyof ThrsModules, MimicDefinition>> = {
  dhw: {
    component: defineAsyncComponent(
      () => import("@/modules/heat/mimics/modules/dhw/DhwModule.vue"),
    ),
    legend: defineAsyncComponent(
      () => import("@/modules/heat/components/legends/DhwLegend.vue"),
    ),
    data: DHW_MIMIC_DATA,
  },
  thrusters: {
    component: defineAsyncComponent(
      () => import("@/modules/heat/mimics/modules/thrusters/ThrustersModule.vue"),
    ),
    legend: defineAsyncComponent(
      () => import("@/modules/heat/components/legends/DhwLegend.vue"),
    ),
    data: THRUSTERS_MIMIC_DATA,
  },
  pvt: {
    component: defineAsyncComponent(
      () => import("@/modules/heat/mimics/modules/pvt/PvtModule.vue"),
    ),
    legend: defineAsyncComponent(
      () => import("@/modules/heat/components/legends/DhwLegend.vue"),
    ),
    data: PVT_MIMIC_DATA,
  },
  pcm: {
    component: defineAsyncComponent(
      () => import("@/modules/heat/mimics/modules/pcm/PcmModule.vue"),
    ),
    legend: defineAsyncComponent(
      () => import("@/modules/heat/components/legends/DhwLegend.vue"),
    ),
    data: PCM_MIMIC_DATA,
  },
  dc: {
    component: defineAsyncComponent(
      () => import("@/modules/heat/mimics/modules/dc/DcModule.vue"),
    ),
    legend: defineAsyncComponent(
      () => import("@/modules/heat/components/legends/DhwLegend.vue"),
    ),
    data: DC_MIMIC_DATA,
  },
  drives: {
    component: defineAsyncComponent(
      () => import("@/modules/heat/mimics/modules/drives/DrivesModule.vue"),
    ),
    legend: defineAsyncComponent(
      () => import("@/modules/heat/components/legends/DhwLegend.vue"),
    ),
    data: DRIVES_MIMIC_DATA,
  },
};
