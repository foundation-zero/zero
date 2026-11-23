<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { OwnersBiminiOutline } from "../../../components/bimini-outline";
import { getTooltipContext } from "../../../data";
import { SolarPanelStringInstance } from "../../../instances";
import { OWNERS_BIMINI_STRINGS } from "../layout";

const getPvtString = getTooltipContext(MimicComponentType.PvtString);

// The top-down view of the owners bimini, without overlays: those belong to the interactive bimini.
const strings = OWNERS_BIMINI_STRINGS.map(({ string, ...layout }) => ({
  ...layout,
  ...getPvtString(`pvt:owners-string-${string}` as Parameters<typeof getPvtString>[0]),
}));
</script>

<template>
  <g>
    <OwnersBiminiOutline />
    <SolarPanelStringInstance
      v-for="(string, index) in strings"
      :key="index"
      v-bind="string"
    />
  </g>
</template>
