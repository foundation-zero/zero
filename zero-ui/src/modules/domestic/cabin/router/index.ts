import { defineAsyncComponent } from "vue";
import { RouteRecordRaw } from "vue-router";
import { waitForRoom } from "../router/guards";

export const cabinRoutes: RouteRecordRaw = {
  path: "cabin",
  name: "cabin",
  meta: {
    layout: defineAsyncComponent(
      () => import("@/modules/domestic/cabin/layouts/DefaultLayout.vue"),
    ),
    beforeResolve: waitForRoom,
  },
  children: [
    {
      path: "airconditioning",
      name: "cabin:airconditioning",
      component: () => import("@/modules/domestic/cabin/views/Airco.vue"),
    },
    {
      path: "lights",
      name: "cabin:lights",
      component: () => import("@/modules/domestic/cabin/views/Lights.vue"),
    },
    {
      path: "blinds",
      name: "cabin:blinds",
      component: () => import("@/modules/domestic/cabin/views/Blinds.vue"),
    },
  ],
};
