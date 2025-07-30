import PlainLayout from "@/layouts/PlainLayout.vue";
import Hmi from "@/views/thrs/Hmi.vue";
import { RouteRecordRaw } from "vue-router";

export const routes: RouteRecordRaw[] = [
  {
    path: "/thrs",
    name: "thrs",
    meta: { layout: PlainLayout, requiresAuth: false },
    component: Hmi,
  },
];
