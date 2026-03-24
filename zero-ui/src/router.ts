import { createRouter, createWebHistory } from "vue-router";
import { sharedRoutes } from "./modules/common/router";
import { domesticRoutes } from "./modules/domestic/router";
import { loadsRoutes } from "./modules/loads/router";
import { thrsRoutes } from "./modules/thrs/router";

const router = createRouter({
  history: createWebHistory(),
  routes: [sharedRoutes, thrsRoutes, domesticRoutes, loadsRoutes],
});

export default router;
