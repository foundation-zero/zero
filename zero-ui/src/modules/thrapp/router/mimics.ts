import { ThrsModules } from "@/modules/thrsim/lib/consts";
import { Component, defineAsyncComponent } from "vue";

export type MimicKey = keyof ThrsModules | "pvt-aft";

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
  "pvt-aft": {
    component: defineAsyncComponent(
      () => import("@/modules/thrapp/mimics/modules/pvt-aft/PvtAftModule.vue"),
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
