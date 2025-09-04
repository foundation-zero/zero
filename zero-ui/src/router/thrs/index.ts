import { defineAsyncComponent } from "vue";
import { RouteRecordRaw } from "vue-router";

export const thrsRoutes: RouteRecordRaw = {
  path: "/thrs",
  name: "thrs",
  meta: {
    layout: defineAsyncComponent(() => import("@/layouts/PlainLayout.vue")),
    requiresAuth: false,
  },
  component: () => import("@/views/thrs/Hmi.vue"),
};
