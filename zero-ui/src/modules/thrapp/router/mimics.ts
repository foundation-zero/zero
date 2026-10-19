import { ThrsModules } from "@/modules/thrsim/lib/consts";
import { Component, defineAsyncComponent } from "vue";

export type MimicDefinition = {
  component: Component;
  legend?: Component;
};

export const MIMICS: Partial<Record<keyof ThrsModules, MimicDefinition>> = {
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
