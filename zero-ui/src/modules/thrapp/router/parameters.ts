import { ThrsModules } from "@/modules/thrapp/lib/consts";
import * as Queries from "@/modules/thrapp/lib/queries.consts";
import { TypedDocumentNode } from "@urql/vue";
import { Component, defineAsyncComponent } from "vue";

export type ParametersDefinition = {
  component: Component;
  /** Query for the data the parameters view shows, polled while it is open. */
  query: TypedDocumentNode;
};

export const PARAMETERS: Partial<Record<keyof ThrsModules, ParametersDefinition>> = {
  adsorption: {
    component: defineAsyncComponent(
      () => import("@/modules/thrapp/parameters/modules/adsorption/AdsorptionParameters.vue"),
    ),
    query: Queries.ADSORPTION_PARAMETERS_PAGE_QUERY,
  },
  dhw: {
    component: defineAsyncComponent(
      () => import("@/modules/thrapp/parameters/modules/dhw/DhwParameters.vue"),
    ),
    query: Queries.DHW_PARAMETERS_PAGE_QUERY,
  },
  thrusters: {
    component: defineAsyncComponent(
      () => import("@/modules/thrapp/parameters/modules/thrusters/ThrustersParameters.vue"),
    ),
    query: Queries.THRUSTERS_PARAMETERS_PAGE_QUERY,
  },
  pvt: {
    component: defineAsyncComponent(
      () => import("@/modules/thrapp/parameters/modules/pvt/PvtParameters.vue"),
    ),
    query: Queries.PVT_PARAMETERS_PAGE_QUERY,
  },
  pcm: {
    component: defineAsyncComponent(
      () => import("@/modules/thrapp/parameters/modules/pcm/PcmParameters.vue"),
    ),
    query: Queries.PCM_PARAMETERS_PAGE_QUERY,
  },
  dc: {
    component: defineAsyncComponent(
      () => import("@/modules/thrapp/parameters/modules/dc/DcParameters.vue"),
    ),
    query: Queries.DC_PARAMETERS_PAGE_QUERY,
  },
  drives: {
    component: defineAsyncComponent(
      () => import("@/modules/thrapp/parameters/modules/drives/DrivesParameters.vue"),
    ),
    query: Queries.DRIVES_PARAMETERS_PAGE_QUERY,
  },
};
