<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { getTooltipContexts } from "../../../data";
import { PvtStringInstance } from "../../../instances";

const pvtStrings = getTooltipContexts(MimicComponentType.PvtString, [
  "pvt:owners-string-1",
  "pvt:owners-string-2",
  "pvt:owners-string-3",
  "pvt:owners-string-4",
  "pvt:owners-string-5",
  "pvt:owners-string-6",
]);
</script>

<template>
  <g>
    <PvtStringInstance
      x="38"
      y="278"
      v-bind="pvtStrings['pvt:owners-string-1']"
    />
    <PvtStringInstance
      x="164"
      y="278"
      v-bind="pvtStrings['pvt:owners-string-2']"
    />
    <PvtStringInstance
      x="290"
      y="278"
      v-bind="pvtStrings['pvt:owners-string-3']"
    />
    <PvtStringInstance
      x="416"
      y="278"
      v-bind="pvtStrings['pvt:owners-string-4']"
    />
    <PvtStringInstance
      x="542"
      y="278"
      v-bind="pvtStrings['pvt:owners-string-5']"
    />
    <PvtStringInstance
      x="668"
      y="278"
      v-bind="pvtStrings['pvt:owners-string-6']"
    />
  </g>
</template>
