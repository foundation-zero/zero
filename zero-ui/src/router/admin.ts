import { Roles } from "@/@types";
import Admin from "@/layouts/AdminLayout.vue";
import CO2Settings from "@modules/environment/co2-settings/CO2Settings.vue";
import HumiditySettings from "@modules/environment/humidity-settings/HumiditySettings.vue";
import { RouteRecordRaw } from "vue-router";

export const envRoutes: RouteRecordRaw[] = [
  {
    path: "/environment",
    name: "environment",
    meta: { layout: Admin, role: Roles.Admin },
    children: [
      {
        path: "overview",
        name: "env:overview",
        component: async () => await import("@/views/environment/Overview.vue"),
      },
      {
        path: "temperature",
        name: "env:temperature",
        component: async () => await import("@/views/environment/Temperature.vue"),
      },
      {
        path: "ventilation",
        name: "env:ventilation",
        component: async () => await import("@/views/environment/Ventilation.vue"),
        meta: { settings: CO2Settings },
      },
      {
        path: "lights",
        name: "env:lights",
        component: async () => await import("@/views/environment/Lights.vue"),
      },
      {
        path: "humidity",
        name: "env:humidity",
        component: async () => await import("@/views/environment/Humidity.vue"),
        meta: { settings: HumiditySettings },
      },
    ],
  },
];
