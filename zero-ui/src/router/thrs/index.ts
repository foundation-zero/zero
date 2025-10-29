import { defineAsyncComponent } from "vue";
import { RouteRecordRaw } from "vue-router";

const thrsChildRoutes: RouteRecordRaw[] = [
  {
    path: "hmi",
    name: "thrs/hmi",
    meta: {
      layout: defineAsyncComponent(() => import("@/layouts/HMILayout.vue")),
      requiresAuth: false,
    },
    redirect: () => ({ name: "thrs/hmi/controls", query: {} }),
    component: () => import("@/views/thrs/Hmi.vue"),
    children: [
      {
        path: "controls",
        name: "thrs/hmi/controls",
        component: () => import("@/views/thrs/Controls.vue"),
      },
      {
        path: "simulation",
        name: "thrs/hmi/simulation",
        component: () => import("@/views/thrs/Simulation.vue"),
      },
      {
        path: "parameters",
        name: "thrs/hmi/parameters",
        component: () => import("@/views/thrs/Parameters.vue"),
      },
      {
        path: "sensors",
        name: "thrs/hmi/sensors",
        component: () => import("@/views/thrs/Sensors.vue"),
      },
    ],
  },
  {
    path: "",
    name: "thrs",
    meta: {
      layout: defineAsyncComponent(() => import("@/layouts/THRSLayout.vue")),
      requiresAuth: false,
    },
    component: () => import("@/components/modules/thrs/Schema.vue"),
  },
];

export const thrsRoutes: RouteRecordRaw = {
  path: "/thrs",
  redirect: () => ({ name: "thrs/hmi", query: {} }),
  children: thrsChildRoutes,
};
