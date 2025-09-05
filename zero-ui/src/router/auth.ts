import EmptyLayout from "@/layouts/EmptyLayout.vue";
import { useAuthStore } from "@/stores/auth";
import { RouteRecordRaw } from "vue-router";

export const authRoutes: RouteRecordRaw = {
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

      return { path: "/domestic" };
    } catch {
      return true;
    }
  },
};
