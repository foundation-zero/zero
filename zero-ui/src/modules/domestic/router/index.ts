import { RouteRecordRaw } from "vue-router";
import { envRoutes } from "../admin/router";
import { cabinRoutes } from "../cabin/router";
import { useAuthStore } from "../stores/auth";
import { authRoutes } from "./auth";

export const domesticRoutes: RouteRecordRaw = {
  path: "/domestic",
  redirect: () => {
    const { isAdmin } = useAuthStore();

    return { name: isAdmin ? "env:temperature" : "cabin:airconditioning", query: {} };
  },
  children: [cabinRoutes, envRoutes, authRoutes],
};
