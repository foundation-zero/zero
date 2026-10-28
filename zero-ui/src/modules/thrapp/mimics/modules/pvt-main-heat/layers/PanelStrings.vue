<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { Ratio } from "@/modules/thrapp/types/thrs";
import { useIntervalFn, useTimeoutFn } from "@vueuse/core";
import { ref } from "vue";
import { getTooltipContext } from "../../../data";
import { SolarPanelStringInstance } from "../../../instances";
import { MAIN_BIMINI_STRINGS } from "../layout";

const getPvtString = getTooltipContext(MimicComponentType.PvtString);

const strings = MAIN_BIMINI_STRINGS.map(({ string, ...layout }) => ({
  string,
  props: {
    ...layout,
    ...getPvtString(`pvt:aft-string-${string}` as Parameters<typeof getPvtString>[0]),
  },
}));

// There is no per-string yield datapoint yet. Until there is, the panels alternate between no yield
// and the relative yields from the Figma yield design (accent-b steps, 1000 = 0 and 0 = 1).
const DESIGN_YIELDS: Record<string, Ratio> = {
  "1.1": 0.9,
  "1.2": 0.9,
  "2.1": 1,
  "2.2": 1,
  "3": 0.8,
  "4": 0.3,
  "5.1": 0.7,
  "5.2": 0.7,
  "6.1": 0.6,
  "6.2": 0.6,
  "7.1": 0.5,
  "7.2": 0.5,
  "8.1": 0.4,
  "8.2": 0.4,
  "9": 0.2,
  "10": 0.1,
  "11.1": 0,
  "11.2": 0,
  "12": 0,
  "13": 0,
};

const showDesignYields = ref(false);
const toggle = () => (showDesignYields.value = !showDesignYields.value);
useIntervalFn(toggle, 10_000);
useTimeoutFn(toggle, 100);
</script>

<template>
  <g>
    <SolarPanelStringInstance
      v-for="({ string, props }, index) in strings"
      :key="index"
      v-bind="props"
      :yield-ratio="showDesignYields ? DESIGN_YIELDS[string] : 0"
    />
  </g>
</template>
