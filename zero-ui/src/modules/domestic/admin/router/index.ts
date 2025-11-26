import { Roles } from "@/modules/domestic/types";
import { defineAsyncComponent } from "vue";
import { RouteRecordRaw } from "vue-router";

export const envRoutes: RouteRecordRaw = {
  path: "environment",
  name: "environment",
  meta: {
    layout: defineAsyncComponent(
      () => import("@/modules/domestic/admin/layouts/DefaultLayout.vue"),
    ),
    role: Roles.Admin,
  },
  children: [
    {
      path: "overview",
      name: "env:overview",
      component: () => import("@/modules/domestic/admin/views/Overview.vue"),
    },
    {
      path: "temperature",
      name: "env:temperature",
      component: () => import("@/modules/domestic/admin/views/Temperature.vue"),
    },
    {
      path: "ventilation",
      name: "env:ventilation",
      component: () => import("@/modules/domestic/admin/views/Ventilation.vue"),
      meta: {
        settings: defineAsyncComponent(
          () => import("@/modules/domestic/admin/components/co2-settings/CO2Settings.vue"),
        ),
      },
    },
    {
      path: "lights",
      name: "env:lights",
      component: () => import("@/modules/domestic/admin/views/Lights.vue"),
    },
    {
      path: "humidity",
      name: "env:humidity",
      component: () => import("@/modules/domestic/admin/views/Humidity.vue"),
      meta: {
        settings: defineAsyncComponent(
          () =>
            import("@/modules/domestic/admin/components/humidity-settings/HumiditySettings.vue"),
        ),
      },
    },
  ],
};
