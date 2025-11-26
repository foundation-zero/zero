import { defineAsyncComponent } from "vue";
import { RouteRecordRaw } from "vue-router";

const thrsChildRoutes: RouteRecordRaw[] = [
  {
    path: "hmi",
    name: "thrs/hmi",
    meta: {
      layout: defineAsyncComponent(() => import("@/modules/thrs/layouts/HMILayout.vue")),
      requiresAuth: false,
    },
    redirect: () => ({ name: "thrs/hmi/controls", query: {} }),
    component: () => import("@/modules/thrs/views/Hmi.vue"),
    children: [
      {
        path: "controls",
        name: "thrs/hmi/controls",
        component: () => import("@/modules/thrs/views/Controls.vue"),
      },
      {
        path: "simulation",
        name: "thrs/hmi/simulation",
        component: () => import("@/modules/thrs/views/Simulation.vue"),
      },
      {
        path: "parameters",
        name: "thrs/hmi/parameters",
        component: () => import("@/modules/thrs/views/Parameters.vue"),
      },
      {
        path: "sensors",
        name: "thrs/hmi/sensors",
        component: () => import("@/modules/thrs/views/Sensors.vue"),
      },
    ],
  },
];

export const thrsRoutes: RouteRecordRaw = {
  path: "/thrs",
  redirect: () => ({ name: "thrs/hmi", query: {} }),
  children: thrsChildRoutes,
};
