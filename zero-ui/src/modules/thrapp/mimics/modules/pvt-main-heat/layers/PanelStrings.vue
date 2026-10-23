<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { getTooltipContext } from "../../../data";
import { SolarPanelStringInstance } from "../../../instances";
import { MAIN_BIMINI_STRINGS } from "../layout";

const getPvtString = getTooltipContext(MimicComponentType.PvtString);

// The main bimini strings are the PVT AFT strings; there is no per-string yield datapoint yet, so
// the panels are rendered without a yield fill.
const strings = MAIN_BIMINI_STRINGS.map(({ string, ...layout }) => ({
  ...layout,
  ...getPvtString(`pvt:aft-string-${string}` as Parameters<typeof getPvtString>[0]),
}));
</script>

<template>
  <g>
    <SolarPanelStringInstance
      v-for="(string, index) in strings"
      :key="index"
      v-bind="string"
    />
  </g>
</template>
