import { Roles } from "@/@types";
import CO2Settings from "@/components/environment/co2-settings/CO2Settings.vue";
import HumiditySettings from "@/components/environment/humidity-settings/HumiditySettings.vue";
import Admin from "@/layouts/AdminLayout.vue";
import CabinLayout from "@/layouts/CabinLayout.vue";
import { useAuthStore } from "@/stores/auth";
import Airco from "@/views/cabin/Airco.vue";
import Blinds from "@/views/cabin/Blinds.vue";
import Lights from "@/views/cabin/Lights.vue";
import Humidity from "@/views/environment/Humidity.vue";
import Temperature from "@/views/environment/Temperature.vue";
import Ventilation from "@/views/environment/Ventilation.vue";
import { createRouter, createWebHistory, RouteRecordRaw } from "vue-router";
import { waitForRoom } from "./guards";

const envRoutes: RouteRecordRaw[] = [
  {
    path: "/environment",
    name: "environement",
    meta: { layout: Admin, role: Roles.Admin },
    children: [
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
        redirect: { name: "env:temperature" },
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

const cabinRoutes: RouteRecordRaw[] = [
  {
    path: "/cabin",
    name: "cabin",
    meta: { layout: CabinLayout, beforeResolve: waitForRoom },
    children: [
      {
        path: "airconditioning",
        name: "cabin:airconditioning",
        component: Airco,
      },
      {
        path: "lights",
        name: "cabin:lights",
        component: Lights,
      },
      {
        path: "blinds",
        name: "cabin:blinds",
        component: Blinds,
      },
    ],
  },
];

const routes: RouteRecordRaw[] = [
  ...envRoutes,
  ...cabinRoutes,
  {
    path: "/",
    redirect: () => {
      const { isLoggedIn, isAdmin } = useAuthStore();

      if (isLoggedIn) {
        return isAdmin ? { name: "env:temperature" } : { name: "cabin:airconditioning", query: {} };
      }

      return { name: "unauthorised" };
    },
  },
  {
    path: "/auth",
    name: "auth",
    meta: { requiresAuth: false },
    redirect: (to) => {
      const token = to.query.token;

      const { cabin } = useAuthStore().setToken(String(token));

      if (cabin.value) {
        localStorage.setItem("currentRoomId", cabin.value);
      }

      return {
        path: "/",
      };
    },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
