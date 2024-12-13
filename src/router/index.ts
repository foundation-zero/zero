import AircoView from "@/views/Airco.vue";
import { createWebHistory, createRouter } from "vue-router";

const routes = [
  { path: "/airco", component: AircoView },
  { path: "/", component: AircoView },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
