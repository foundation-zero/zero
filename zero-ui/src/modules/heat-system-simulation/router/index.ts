import { defineAsyncComponent } from "vue";
import { RouteRecordRaw } from "vue-router";

export const heatSystemSimulationRoutes: RouteRecordRaw = {
  path: "/heat-system-simulation",
  alias: "/thrsim",
  redirect: () => ({
    name: "heat-system-simulation/mimic",
    query: {},
    params: { module: "dhw" },
  }),
  meta: {
    layout: defineAsyncComponent(() =>
      import("@/modules/heat-system-simulation/layouts/DefaultLayout.vue"),
    ),
    requiresAuth: false,
  },
  children: [
    {
      path: "simulation",
      name: "heat-system-simulation/simulation",
      component: () => import("@/modules/heat-system-simulation/views/Simulation.vue"),
    },
    {
      path: ":module",
      children: [
        {
          path: "controls",
          name: "heat-system-simulation/controls",
          component: () => import("@/modules/heat-system-simulation/views/Controls.vue"),
        },
        {
          path: "monitoring",
          name: "heat-system-simulation/monitoring",
          component: () => import("@/modules/heat-system-simulation/views/Monitoring.vue"),
        },
        {
          path: "parameters",
          name: "heat-system-simulation/parameters",
          component: () => import("@/modules/heat-system-simulation/views/Parameters.vue"),
        },
        {
          path: "mimic",
          name: "heat-system-simulation/mimic",
          component: () => import("@/modules/heat-system/views/Mimic.vue"),
        },
      ],
    },
  ],
};
