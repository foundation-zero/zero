import EmptyLayout from "@/layouts/EmptyLayout.vue";
import { useAuthStore } from "@/stores/auth";
import { createRouter, createWebHistory, RouteRecordRaw } from "vue-router";
import { envRoutes } from "./admin";
import { cabinRoutes } from "./cabin";

const routes: RouteRecordRaw[] = [
  ...envRoutes,
  ...cabinRoutes,
  {
    path: "/",
    redirect: () => {
      const { isAdmin } = useAuthStore();

      return { name: isAdmin ? "env:temperature" : "cabin:airconditioning", query: {} };
    },
  },
  {
    path: "/auth",
    name: "auth",
    meta: { requiresAuth: false, layout: EmptyLayout },
    component: () => import("@/views/Unauthorised.vue"),
    beforeEnter: async (to) => {
      const token = to.query.token;

      if (!token) return true;

      const authStore = useAuthStore();

      const { cabin } = authStore.setToken(String(token));

      try {
        await authStore.verifyToken();

        if (cabin.value) {
          localStorage.setItem("currentRoomId", cabin.value);
        }

        return { path: "/" };
      } catch {
        return true;
      }
    },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
