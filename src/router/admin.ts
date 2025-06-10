import { Roles } from "@/@types";
import CO2Settings from "@/components/environment/co2-settings/CO2Settings.vue";
import HumiditySettings from "@/components/environment/humidity-settings/HumiditySettings.vue";
import Admin from "@/layouts/AdminLayout.vue";
import Humidity from "@/views/environment/Humidity.vue";
import Lights from "@/views/environment/Lights.vue";
import Overview from "@/views/environment/Overview.vue";
import Temperature from "@/views/environment/Temperature.vue";
import Ventilation from "@/views/environment/Ventilation.vue";
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
        component: Overview,
      },
      {
        path: "temperature",
        name: "env:temperature",
        component: Temperature,
      },
      {
        path: "ventilation",
        name: "env:ventilation",
        component: Ventilation,
        meta: { settings: CO2Settings },
      },
      {
        path: "lights",
        name: "env:lights",
        component: Lights,
      },
      {
        path: "humidity",
        name: "env:humidity",
        component: Humidity,
        meta: { settings: HumiditySettings },
      },
    ],
  },
];
