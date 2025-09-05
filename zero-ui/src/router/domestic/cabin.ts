import { defineAsyncComponent } from "vue";
import { RouteRecordRaw } from "vue-router";
import { waitForRoom } from "./guards";

export const cabinRoutes: RouteRecordRaw = {
  path: "cabin",
  name: "cabin",
  meta: {
    layout: defineAsyncComponent(() => import("@/layouts/CabinLayout.vue")),
    beforeResolve: waitForRoom,
  },
  children: [
    {
      path: "airconditioning",
      name: "cabin:airconditioning",
      component: () => import("@/views/cabin/Airco.vue"),
    },
    {
      path: "lights",
      name: "cabin:lights",
      component: () => import("@/views/cabin/Lights.vue"),
    },
    {
      path: "blinds",
      name: "cabin:blinds",
      component: () => import("@/views/cabin/Blinds.vue"),
    },
  ],
};
