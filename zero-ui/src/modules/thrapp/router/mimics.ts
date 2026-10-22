import { ThrsModules } from "@/modules/thrsim/lib/consts";
import { Component, defineAsyncComponent } from "vue";

export type MimicKey = keyof ThrsModules | "pvt-aft" | "pvt-bimini";

export type MimicDefinition = {
  component: Component;
  legend?: Component;
  /** The thrsim module backing this mimic, if it differs from the mimic key. */
  module?: keyof ThrsModules;
};

export const MIMICS: Partial<Record<MimicKey, MimicDefinition>> = {
  dhw: {
    component: defineAsyncComponent(
      () => import("@/modules/thrapp/mimics/modules/dhw/DhwModule.vue"),
    ),
    legend: defineAsyncComponent(() => import("@/modules/thrapp/components/legends/DhwLegend.vue")),
  },
  thrusters: {
    component: defineAsyncComponent(
      () => import("@/modules/thrapp/mimics/modules/thrusters/ThrustersModule.vue"),
    ),
    legend: defineAsyncComponent(() => import("@/modules/thrapp/components/legends/DhwLegend.vue")),
  },
  pvt: {
    component: defineAsyncComponent(
      () => import("@/modules/thrapp/mimics/modules/pvt/PvtModule.vue"),
    ),
    legend: defineAsyncComponent(() => import("@/modules/thrapp/components/legends/DhwLegend.vue")),
  },
  "pvt-aft": {
    component: defineAsyncComponent(
      () => import("@/modules/thrapp/mimics/modules/pvt-aft/PvtAftModule.vue"),
    ),
    legend: defineAsyncComponent(() => import("@/modules/thrapp/components/legends/DhwLegend.vue")),
    module: "pvt",
  },
  "pvt-bimini": {
    component: defineAsyncComponent(
      () => import("@/modules/thrapp/mimics/modules/pvt-bimini/PvtBiminiModule.vue"),
    ),
    module: "pvt",
  },
  pcm: {
    component: defineAsyncComponent(
      () => import("@/modules/thrapp/mimics/modules/pcm/PcmModule.vue"),
    ),
    legend: defineAsyncComponent(() => import("@/modules/thrapp/components/legends/DhwLegend.vue")),
  },
  dc: {
    component: defineAsyncComponent(
      () => import("@/modules/thrapp/mimics/modules/dc/DcModule.vue"),
    ),
    legend: defineAsyncComponent(() => import("@/modules/thrapp/components/legends/DhwLegend.vue")),
  },
  drives: {
    component: defineAsyncComponent(
      () => import("@/modules/thrapp/mimics/modules/drives/DrivesModule.vue"),
    ),
    legend: defineAsyncComponent(() => import("@/modules/thrapp/components/legends/DhwLegend.vue")),
  },
};

export const toThrsModule = (key: string): keyof ThrsModules =>
  MIMICS[key as MimicKey]?.module ?? (key as keyof ThrsModules);
