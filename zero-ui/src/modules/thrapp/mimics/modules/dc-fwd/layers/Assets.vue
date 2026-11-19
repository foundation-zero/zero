<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { getTooltipContexts } from "../../../data";
import { PowerConverterInstance } from "../../../instances";

const converters = getTooltipContexts(MimicComponentType.PowerConverter, ["dc:fwd-2", "dc:fwd-1"]);
</script>

<template>
  <g>
    <PowerConverterInstance
      x="0"
      y="0"
      v-bind="converters['dc:fwd-2']"
    />
    <PowerConverterInstance
      x="0"
      y="205"
      v-bind="converters['dc:fwd-1']"
    />
  </g>
</template>
