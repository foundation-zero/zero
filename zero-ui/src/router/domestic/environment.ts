import { Roles } from "@/@types";
import { defineAsyncComponent } from "vue";
import { RouteRecordRaw } from "vue-router";

export const envRoutes: RouteRecordRaw = {
  path: "environment",
  name: "environment",
  meta: {
    layout: defineAsyncComponent(() => import("@/layouts/AdminLayout.vue")),
    role: Roles.Admin,
  },
  children: [
    {
      path: "overview",
      name: "env:overview",
      component: () => import("@/views/environment/Overview.vue"),
    },
    {
      path: "temperature",
      name: "env:temperature",
      component: () => import("@/views/environment/Temperature.vue"),
    },
    {
      path: "ventilation",
      name: "env:ventilation",
      component: () => import("@/views/environment/Ventilation.vue"),
      meta: {
        settings: defineAsyncComponent(
          () => import("@modules/environment/co2-settings/CO2Settings.vue"),
        ),
      },
    },
    {
      path: "lights",
      name: "env:lights",
      component: () => import("@/views/environment/Lights.vue"),
    },
    {
      path: "humidity",
      name: "env:humidity",
      component: () => import("@/views/environment/Humidity.vue"),
      meta: {
        settings: defineAsyncComponent(
          () => import("@modules/environment/humidity-settings/HumiditySettings.vue"),
        ),
      },
    },
  ],
};
