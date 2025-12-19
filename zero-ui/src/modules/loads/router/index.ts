import { defineAsyncComponent } from "vue";
import { RouteRecordRaw } from "vue-router";

const loadsChildRoutes: RouteRecordRaw[] = [
  {
    path: "dashboard",
    name: "loads/dashboard",
    component: () => import("@/modules/loads/views/Dashboard.vue"),
  },
];

export const loadsRoutes: RouteRecordRaw = {
  path: "/loads",
  redirect: () => ({ name: "loads/dashboard", query: {} }),
  meta: {
    layout: defineAsyncComponent(() => import("@/modules/loads/layouts/DefaultLayout.vue")),
    requiresAuth: false,
  },
  children: loadsChildRoutes,
};
