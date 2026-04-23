import { Roles } from "@/modules/domestic/types";
import { defineAsyncComponent } from "vue";
import { RouteRecordRaw } from "vue-router";

export const envRoutes: RouteRecordRaw = {
  path: "environment",
  name: "environment",
  meta: {
    mainNav: defineAsyncComponent(() => import("@/modules/domestic/admin/components/MainNav.vue")),
    subNav: defineAsyncComponent(() => import("@/modules/domestic/admin/components/SubNav.vue")),
    role: Roles.Admin,
  },
  component: () => import("@/modules/domestic/admin/layouts/DefaultLayout.vue"),
  children: [
    {
      path: "control",
      name: "environment:control",
      component: () => import("@/modules/domestic/admin/views/Overview.vue"),
    },
    {
      path: "temperature",
      name: "environment:temperature",
      component: () => import("@/modules/domestic/admin/views/Temperature.vue"),
    },
    {
      path: "ventilation",
      name: "environment:ventilation",
      component: () => import("@/modules/domestic/admin/views/Ventilation.vue"),
      meta: {
        settings: defineAsyncComponent(
          () => import("@/modules/domestic/admin/components/co2-settings/CO2Settings.vue"),
        ),
      },
    },
    {
      path: "lights",
      name: "environment:lights",
      component: () => import("@/modules/domestic/admin/views/Lights.vue"),
    },
    {
      path: "humidity",
      name: "environment:humidity",
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
