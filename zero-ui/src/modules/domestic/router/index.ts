import { defineAsyncComponent } from "vue";
import { RouteRecordRaw } from "vue-router";
import { envRoutes } from "../admin/router";
import { cabinRoutes } from "../cabin/router";
import { useAuthStore } from "../stores/auth";
import { authRoutes } from "./auth";

export const domesticRoutes: RouteRecordRaw = {
  path: "/domestic",
  meta: {
    layout: defineAsyncComponent(() => import("@/modules/domestic/layouts/DefaultLayout.vue")),
  },
  redirect: () => {
    const { isAdmin } = useAuthStore();

    return { name: isAdmin ? "environment:control" : "cabin:airconditioning", query: {} };
  },
  children: [cabinRoutes, envRoutes, authRoutes],
};
