<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { getTooltipContexts } from "../../../data";
import { DcConverterInstance } from "../../../instances";

const converters = getTooltipContexts(MimicComponentType.DcConverter, [
  "dc:aft",
  "dc:ugrid",
  "dc:fwd",
]);
</script>

<template>
  <DcConverterInstance
    x="19"
    y="28"
    v-bind="converters['dc:aft']"
  />
  <DcConverterInstance
    x="19"
    y="260"
    v-bind="converters['dc:ugrid']"
  />
  <DcConverterInstance
    x="19"
    y="498"
    v-bind="converters['dc:fwd']"
  />
</template>
