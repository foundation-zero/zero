import { defineAsyncComponent } from "vue";
import { RouteRecordRaw } from "vue-router";

const alarmChildRoutes: RouteRecordRaw[] = [
  {
    path: "",
    name: "alarms/list",
    component: () => import("@/modules/alarms/views/Alarms.vue"),
  },
];

export const alarmRoutes: RouteRecordRaw = {
  path: "/alarms",
  redirect: () => ({ name: "alarms/list", query: {} }),
  meta: {
    layout: defineAsyncComponent(() => import("@/modules/alarms/layouts/DefaultLayout.vue")),
    requiresAuth: false,
  },
  children: alarmChildRoutes,
};
