import { defineAsyncComponent } from "vue";
import { RouteRecordRaw } from "vue-router";

const powerChildRoutes: RouteRecordRaw[] = [
  {
    path: "",
    name: "power-tags/tags",
    component: () => import("@/modules/power-tags/views/PowerTags.vue"),
  },
];

export const powerRoutes: RouteRecordRaw = {
  path: "/power-tags",
  redirect: () => ({ name: "power-tags/tags", query: {} }),
  meta: {
    layout: defineAsyncComponent(() => import("@/modules/power-tags/layouts/DefaultLayout.vue")),
    requiresAuth: false,
  },
  children: powerChildRoutes,
};
