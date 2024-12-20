import Airco from "@/views/Airco.vue";
import Lights from "@/views/Lights.vue";
import Blinds from "@/views/Blinds.vue";
import { createWebHistory, createRouter } from "vue-router";

const routes = [
  { path: "/airco", component: Airco },
  { path: "/lights", component: Lights },
  { path: "/blinds", component: Blinds },
  { path: "/", component: Airco },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
