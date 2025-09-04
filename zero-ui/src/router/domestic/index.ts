import { useAuthStore } from "@/stores/auth";
import { RouteRecordRaw } from "vue-router";
import { cabinRoutes } from "./cabin";
import { envRoutes } from "./environment";

export const domesticRoutes: RouteRecordRaw = {
  path: "/domestic",
  redirect: () => {
    const { isAdmin } = useAuthStore();

    return { name: isAdmin ? "env:temperature" : "cabin:airconditioning", query: {} };
  },
  children: [cabinRoutes, envRoutes],
};
