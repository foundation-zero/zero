import { defineAsyncComponent } from "vue";
import { RouteRecordRaw } from "vue-router";

export const sharedRoutes: RouteRecordRaw = {
  path: "/",
  meta: {
    requiresAuth: false,
    layout: defineAsyncComponent(() => import("../layouts/SplashLayout.vue")),
  },
  component: () => import("@/modules/common/views/SplashScreen.vue"),
};
