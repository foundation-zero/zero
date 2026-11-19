<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { getTooltipContexts } from "../../../data";
import { PowerConverterInstance } from "../../../instances";

const converters = getTooltipContexts(MimicComponentType.PowerConverter, [
  "dc:aft-4",
  "dc:aft-3",
  "dc:aft-2",
  "dc:aft-1",
]);
</script>

<template>
  <g>
    <PowerConverterInstance
      x="0"
      y="0"
      v-bind="converters['dc:aft-4']"
    />
    <PowerConverterInstance
      x="0"
      y="208"
      v-bind="converters['dc:aft-3']"
    />
    <PowerConverterInstance
      x="0"
      y="416"
      v-bind="converters['dc:aft-2']"
    />
    <PowerConverterInstance
      x="0"
      y="624"
      v-bind="converters['dc:aft-1']"
    />
  </g>
</template>
