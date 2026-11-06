import { defineAsyncComponent } from "vue";
import { RouteRecordRaw } from "vue-router";

const rigChildRoutes: RouteRecordRaw[] = [
  {
    path: "",
    name: "rig/overview",
    component: () => import("@/modules/rig/views/Rig.vue"),
  },
];

export const rigRoutes: RouteRecordRaw = {
  path: "/rig",
  redirect: () => ({ name: "rig/overview", query: {} }),
  meta: {
    layout: defineAsyncComponent(() => import("@/modules/rig/layouts/DefaultLayout.vue")),
    requiresAuth: false,
  },
  children: rigChildRoutes,
};
