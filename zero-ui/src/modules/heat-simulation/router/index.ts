import { defineAsyncComponent } from "vue";
import { RouteRecordRaw } from "vue-router";

export const heatSimulationRoutes: RouteRecordRaw = {
  path: "/heat-simulation",
  alias: ["/heat-system-simulation", "/thrsim"],
  redirect: () => ({
    name: "heat-simulation/mimic",
    query: {},
    params: { module: "dhw" },
  }),
  meta: {
    layout: defineAsyncComponent(() =>
      import("@/modules/heat-simulation/layouts/DefaultLayout.vue"),
    ),
    requiresAuth: false,
  },
  children: [
    {
      path: "simulation",
      name: "heat-simulation/simulation",
      component: () => import("@/modules/heat-simulation/views/Simulation.vue"),
    },
    {
      path: ":module",
      children: [
        {
          path: "controls",
          name: "heat-simulation/controls",
          component: () => import("@/modules/heat-simulation/views/Controls.vue"),
        },
        {
          path: "monitoring",
          name: "heat-simulation/monitoring",
          component: () => import("@/modules/heat-simulation/views/Monitoring.vue"),
        },
        {
          path: "parameters",
          name: "heat-simulation/parameters",
          component: () => import("@/modules/heat-simulation/views/Parameters.vue"),
        },
        {
          path: "mimic",
          name: "heat-simulation/mimic",
          component: () => import("@/modules/heat/views/Mimic.vue"),
        },
      ],
    },
  ],
};
