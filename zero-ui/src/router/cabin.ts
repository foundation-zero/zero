import CabinLayout from "@/layouts/CabinLayout.vue";
import Airco from "@/views/cabin/Airco.vue";
import Blinds from "@/views/cabin/Blinds.vue";
import Lights from "@/views/cabin/Lights.vue";
import { RouteRecordRaw } from "vue-router";
import { waitForRoom } from "./guards";

export const cabinRoutes: RouteRecordRaw[] = [
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
