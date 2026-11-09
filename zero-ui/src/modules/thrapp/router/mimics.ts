import { ThrsModules } from "@/modules/thrapp/lib/consts";
import * as Queries from "@/modules/thrapp/lib/queries.consts";
import { LayerFilterOption } from "@/modules/thrapp/mimics/components/layer-filter/layer-filter.provider";
import { TypedDocumentNode } from "@urql/vue";
import { Component, defineAsyncComponent } from "vue";

export type MimicKey = keyof ThrsModules | "pvt-main" | "pvt-owners" | "pvt-main-heat";

type LayerFilters = Partial<Record<LayerFilterOption, true>>;

export type MimicDefinition = {
  component: Component;
  /** Query for the data the mimic shows, polled while it is open. */
  query: TypedDocumentNode;
  /** Layers the viewer can show or hide; `LAYER_FILTER_OPTIONS` sets their order. */
  layerFilters?: LayerFilters;
};

const BASE_FILTERS: LayerFilters = {
  [LayerFilterOption.SensorValues]: true,
  [LayerFilterOption.YardTags]: true,
  [LayerFilterOption.ManualComponents]: true,
  [LayerFilterOption.DirectionArrows]: true,
};
const SUPPORT_FILTERS: LayerFilters = {
  ...BASE_FILTERS,
  [LayerFilterOption.SupportComponents]: true,
};
const BYPASS_FILTERS: LayerFilters = {
  ...SUPPORT_FILTERS,
  [LayerFilterOption.Bypasses]: true,
};

export const MIMICS: Partial<Record<MimicKey, MimicDefinition>> = {
  dhw: {
    component: defineAsyncComponent(
      () => import("@/modules/thrapp/mimics/modules/dhw/DhwModule.vue"),
    ),
    query: Queries.DHW_MIMIC_QUERY,
    layerFilters: {
      ...BASE_FILTERS,
      [LayerFilterOption.Flows]: true,
      [LayerFilterOption.Bypasses]: true,
    },
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
