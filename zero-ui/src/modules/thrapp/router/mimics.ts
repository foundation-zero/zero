import { ThrsModules } from "@/modules/thrsim/lib/consts";
import { Component, defineAsyncComponent } from "vue";

export type MimicKey = keyof ThrsModules | "pvt-main" | "pvt-owners" | "pvt-main-heat";

export type MimicDefinition = {
  component: Component;
};

export const MIMICS: Partial<Record<MimicKey, MimicDefinition>> = {
  dhw: {
    component: defineAsyncComponent(
      () => import("@/modules/thrapp/mimics/modules/dhw/DhwModule.vue"),
    ),
  },
  thrusters: {
    component: defineAsyncComponent(
      () => import("@/modules/thrapp/mimics/modules/thrusters/ThrustersModule.vue"),
    ),
  },
  pvt: {
    component: defineAsyncComponent(
      () => import("@/modules/thrapp/mimics/modules/pvt/PvtModule.vue"),
    ),
  },
  "pvt-main": {
    component: defineAsyncComponent(
      () => import("@/modules/thrapp/mimics/modules/pvt-main/PvtMainModule.vue"),
    ),
  },
  "pvt-owners": {
    component: defineAsyncComponent(
      () => import("@/modules/thrapp/mimics/modules/pvt-owners/PvtOwnersModule.vue"),
    ),
  },
  "pvt-main-heat": {
    component: defineAsyncComponent(
      () => import("@/modules/thrapp/mimics/modules/pvt-main-heat/PvtMainHeatModule.vue"),
    ),
  },
  pcm: {
    component: defineAsyncComponent(
      () => import("@/modules/thrapp/mimics/modules/pcm/PcmModule.vue"),
    ),
  },
  dc: {
    component: defineAsyncComponent(
      () => import("@/modules/thrapp/mimics/modules/dc/DcModule.vue"),
    ),
  },
  drives: {
    component: defineAsyncComponent(
      () => import("@/modules/thrapp/mimics/modules/drives/DrivesModule.vue"),
    ),
  },
};
