import { useAuthStore } from "@/modules/common/stores/auth";
import EmptyLayout from "@common/layouts/EmptyLayout.vue";
import { RouteRecordRaw } from "vue-router";
import { verifyToken } from "../lib/auth";

export const authRoutes: RouteRecordRaw = {
  path: "auth",
  name: "domestic:auth",
  meta: { requiresAuth: false, layout: EmptyLayout },
  component: () => import("@common/views/Unauthorised.vue"),
  beforeEnter: async (to) => {
    const token = to.query.token;

    if (!token) return true;

    const authStore = useAuthStore();

    const { cabin } = authStore.setToken(String(token));

    try {
      await verifyToken();

      if (cabin.value) {
        localStorage.setItem("currentRoomId", cabin.value);
      }

      return { path: "/domestic" };
    } catch {
      return true;
    }
  },
};
