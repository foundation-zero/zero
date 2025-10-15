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
    component: () => import("@/views/thrs/Hmi.vue"),
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
