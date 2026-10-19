<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { getTooltipContexts } from "../../../data";
import {
  ExpansionTankInstance,
  ExpansionValveInstance,
  TagLabelInstance,
} from "../../../instances";

const expansionTanks = getTooltipContexts(MimicComponentType.ExpansionTank, ["1040-04"]);
const expansionValves = getTooltipContexts(MimicComponentType.ExpansionValve, ["1041-05"]);
</script>

<template>
  <g>
    <ExpansionTankInstance
      x="1612"
      y="102"
      v-bind="expansionTanks['1040-04']"
    />
    <TagLabelInstance
      x="1568"
      y="118"
      tag-id="1040-04"
    />
    <g transform="matrix(0 1 1 0 1657 71)">
      <ExpansionValveInstance v-bind="expansionValves['1041-05']" />
    </g>
    <TagLabelInstance
      x="1607"
      y="69"
      tag-id="1041-05"
    />
  </g>
</template>
