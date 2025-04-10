import { useAuthStore } from "@/stores/auth";
import Airco from "@/views/Airco.vue";
import Blinds from "@/views/Blinds.vue";
import Lights from "@/views/Lights.vue";
import { createRouter, createWebHistory, RouteRecordRaw } from "vue-router";

const routes: RouteRecordRaw[] = [
  { path: "/airco", component: Airco },
  { path: "/lights", component: Lights },
  { path: "/blinds", component: Blinds },
  { path: "/", component: Airco },
  {
    path: "/auth",
    redirect: (to) => {
      const authStore = useAuthStore();
      const token = to.query.token;
      authStore.setToken(token as string);

      return { path: "/", query: {} };
    },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
