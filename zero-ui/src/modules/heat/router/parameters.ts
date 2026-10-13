import { ThrsModules } from "@/modules/heat-simulation/lib/consts";
import { Component, defineAsyncComponent } from "vue";

export const PARAMETERS: Partial<Record<keyof ThrsModules, Component>> = {
  adsorption: defineAsyncComponent(
    () => import("@/modules/heat/parameters/modules/adsorption/AdsorptionParameters.vue"),
  ),
  dhw: defineAsyncComponent(
    () => import("@/modules/heat/parameters/modules/dhw/DhwParameters.vue"),
  ),
  thrusters: defineAsyncComponent(
    () => import("@/modules/heat/parameters/modules/thrusters/ThrustersParameters.vue"),
  ),
  pvt: defineAsyncComponent(
    () => import("@/modules/heat/parameters/modules/pvt/PvtParameters.vue"),
  ),
  pcm: defineAsyncComponent(
    () => import("@/modules/heat/parameters/modules/pcm/PcmParameters.vue"),
  ),
  dc: defineAsyncComponent(
    () => import("@/modules/heat/parameters/modules/dc/DcParameters.vue"),
  ),
  drives: defineAsyncComponent(
    () => import("@/modules/heat/parameters/modules/drives/DrivesParameters.vue"),
  ),
};
