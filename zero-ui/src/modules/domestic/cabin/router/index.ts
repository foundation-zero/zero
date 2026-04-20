import { attachReturnUrlGuard } from "@/guards";
import { defineAsyncComponent } from "vue";
import { RouteRecordRaw } from "vue-router";
import { waitForRoom } from "../router/guards";

export const cabinRoutes: RouteRecordRaw = {
  path: "cabin",
  name: "cabin",
  component: () => import("@/modules/domestic/cabin/layouts/DefaultLayout.vue"),
  beforeEnter: attachReturnUrlGuard,
  meta: {
    hideAppSwitcher: true,
    subNav: defineAsyncComponent(() => import("@/modules/domestic/cabin/components/SubNav.vue")),
    bottomNav: defineAsyncComponent(
      () => import("@/modules/domestic/cabin/components/BottomNavigation.vue"),
    ),
    beforeResolve: waitForRoom,
  },
  children: [
    {
      path: "air-conditioning",
      name: "cabin:air-conditioning",
      beforeEnter: attachReturnUrlGuard,
      component: () => import("@/modules/domestic/cabin/views/Airco.vue"),
    },
    {
      path: "lights",
      name: "cabin:lights",
      beforeEnter: attachReturnUrlGuard,
      component: () => import("@/modules/domestic/cabin/views/Lights.vue"),
    },
    {
      path: "blinds",
      name: "cabin:blinds",
      beforeEnter: attachReturnUrlGuard,
      component: () => import("@/modules/domestic/cabin/views/Blinds.vue"),
    },
  ],
};
