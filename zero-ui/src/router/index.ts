import { createRouter, createWebHistory } from "vue-router";
import { authRoutes } from "./auth";
import { domesticRoutes } from "./domestic";
import { thrsRoutes } from "./thrs";

const router = createRouter({
  history: createWebHistory(),
  routes: [thrsRoutes, domesticRoutes, authRoutes],
});

export default router;
