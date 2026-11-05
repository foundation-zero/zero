import { ThrsModules } from "@/modules/thrapp/lib/consts";
import * as Queries from "@/modules/thrapp/lib/queries.consts";
import { LayerFilterOption } from "@/modules/thrapp/mimics/components/layer-filter/layer-filter.provider";
import { TypedDocumentNode } from "@urql/vue";
import { Component, defineAsyncComponent } from "vue";

export type MimicKey = keyof ThrsModules | "pvt-main" | "pvt-owners" | "pvt-main-heat";

export type MimicDefinition = {
  component: Component;
  /** Query for the data the mimic shows, polled while it is open. */
  query: TypedDocumentNode;
  /** Layers the viewer can show or hide, in display order. */
  layerFilters?: LayerFilterOption[];
};

const BASE_FILTERS = [LayerFilterOption.ManualComponents, LayerFilterOption.DirectionArrows];
const SUPPORT_FILTERS = [
  LayerFilterOption.ManualComponents,
  LayerFilterOption.SupportComponents,
  LayerFilterOption.DirectionArrows,
];

const BYPASS_FILTERS = [
  LayerFilterOption.ManualComponents,
  LayerFilterOption.Bypasses,
  LayerFilterOption.SupportComponents,
  LayerFilterOption.DirectionArrows,
];

export const MIMICS: Partial<Record<MimicKey, MimicDefinition>> = {
  dhw: {
    component: defineAsyncComponent(
      () => import("@/modules/thrapp/mimics/modules/dhw/DhwModule.vue"),
    ),
    query: Queries.DHW_MIMIC_QUERY,
    layerFilters: [
      LayerFilterOption.ManualComponents,
      LayerFilterOption.Bypasses,
      LayerFilterOption.Flows,
      LayerFilterOption.DirectionArrows,
    ],
  },
  thrusters: {
    component: defineAsyncComponent(
      () => import("@/modules/thrapp/mimics/modules/thrusters/ThrustersModule.vue"),
    ),
    query: Queries.THRUSTERS_MIMIC_QUERY,
    layerFilters: SUPPORT_FILTERS,
  },
  pvt: {
    component: defineAsyncComponent(
      () => import("@/modules/thrapp/mimics/modules/pvt/PvtModule.vue"),
    ),
    query: Queries.PVT_MIMIC_QUERY,
    layerFilters: BYPASS_FILTERS,
  },
  "pvt-main": {
    component: defineAsyncComponent(
      () => import("@/modules/thrapp/mimics/modules/pvt-main/PvtMainModule.vue"),
    ),
    query: Queries.PVT_SECTION_MIMIC_QUERY,
    layerFilters: BASE_FILTERS,
  },
  "pvt-owners": {
    component: defineAsyncComponent(
      () => import("@/modules/thrapp/mimics/modules/pvt-owners/PvtOwnersModule.vue"),
    ),
    query: Queries.PVT_SECTION_MIMIC_QUERY,
    layerFilters: BASE_FILTERS,
  },
  "pvt-main-heat": {
    component: defineAsyncComponent(
      () => import("@/modules/thrapp/mimics/modules/pvt-main-heat/PvtMainHeatModule.vue"),
    ),
    query: Queries.PVT_SECTION_MIMIC_QUERY,
  },
  pcm: {
    component: defineAsyncComponent(
      () => import("@/modules/thrapp/mimics/modules/pcm/PcmModule.vue"),
    ),
    query: Queries.PCM_MIMIC_QUERY,
    layerFilters: BASE_FILTERS,
  },
  dc: {
    component: defineAsyncComponent(
      () => import("@/modules/thrapp/mimics/modules/dc/DcModule.vue"),
    ),
    query: Queries.DC_MIMIC_QUERY,
    layerFilters: BYPASS_FILTERS,
  },
  adsorption: {
    component: defineAsyncComponent(
      () => import("@/modules/thrapp/mimics/modules/adsorption/AdsorptionModule.vue"),
    ),
    query: Queries.ADSORPTION_MIMIC_QUERY,
    layerFilters: SUPPORT_FILTERS,
  },
  drives: {
    component: defineAsyncComponent(
      () => import("@/modules/thrapp/mimics/modules/drives/DrivesModule.vue"),
    ),
    query: Queries.DRIVES_MIMIC_QUERY,
    layerFilters: BYPASS_FILTERS,
  },
};
