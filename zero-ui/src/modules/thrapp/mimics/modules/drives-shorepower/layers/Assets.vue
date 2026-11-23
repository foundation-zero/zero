<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { getTooltipContexts } from "../../../data";
import { PowerConverterInstance } from "../../../instances";

const converters = getTooltipContexts(MimicComponentType.PowerConverter, [
  "drives:shorepower-1a",
  "drives:shorepower-1b",
  "drives:shorepower-2a",
  "drives:shorepower-2b",
]);
</script>

<template>
  <g>
    <PowerConverterInstance
      x="40.63"
      y="23.41"
      width="198"
      v-bind="converters['drives:shorepower-1a']"
    />
    <PowerConverterInstance
      x="40.63"
      y="230.41"
      width="198"
      v-bind="converters['drives:shorepower-1b']"
    />
    <PowerConverterInstance
      x="40.63"
      y="437.41"
      width="198"
      v-bind="converters['drives:shorepower-2a']"
    />
    <PowerConverterInstance
      x="40.63"
      y="644.41"
      width="198"
      v-bind="converters['drives:shorepower-2b']"
    />
  </g>
</template>
