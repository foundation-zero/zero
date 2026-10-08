import { ThrsModules } from "@/modules/thrsim/lib/consts";
import { Component, defineAsyncComponent } from "vue";

export const PARAMETERS: Partial<Record<keyof ThrsModules, Component>> = {
  dhw: defineAsyncComponent(
    () => import("@/modules/thrapp/parameters/modules/dhw/DhwParameters.vue"),
  ),
  thrusters: defineAsyncComponent(
    () => import("@/modules/thrapp/parameters/modules/thrusters/ThrustersParameters.vue"),
  ),
};
