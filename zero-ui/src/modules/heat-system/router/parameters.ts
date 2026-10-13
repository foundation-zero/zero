import { ThrsModules } from "@/modules/heat-system-simulation/lib/consts";
import { Component, defineAsyncComponent } from "vue";

export const PARAMETERS: Partial<Record<keyof ThrsModules, Component>> = {
  adsorption: defineAsyncComponent(
    () => import("@/modules/heat-system/parameters/modules/adsorption/AdsorptionParameters.vue"),
  ),
  dhw: defineAsyncComponent(
    () => import("@/modules/heat-system/parameters/modules/dhw/DhwParameters.vue"),
  ),
  thrusters: defineAsyncComponent(
    () => import("@/modules/heat-system/parameters/modules/thrusters/ThrustersParameters.vue"),
  ),
  pvt: defineAsyncComponent(
    () => import("@/modules/heat-system/parameters/modules/pvt/PvtParameters.vue"),
  ),
  pcm: defineAsyncComponent(
    () => import("@/modules/heat-system/parameters/modules/pcm/PcmParameters.vue"),
  ),
  dc: defineAsyncComponent(
    () => import("@/modules/heat-system/parameters/modules/dc/DcParameters.vue"),
  ),
  drives: defineAsyncComponent(
    () => import("@/modules/heat-system/parameters/modules/drives/DrivesParameters.vue"),
  ),
};
