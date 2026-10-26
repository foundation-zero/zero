<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { getTooltipContexts } from "../../../data";
import {
  ExpansionTankInstance,
  ExpansionValveInstance,
  TagLabelInstance,
} from "../../../instances";

const expansionTanks = getTooltipContexts(MimicComponentType.ExpansionTank, ["1040-01"]);
const expansionValves = getTooltipContexts(MimicComponentType.ExpansionValve, ["1041-01"]);
</script>

<template>
  <ExpansionTankInstance
    x="1215"
    y="165"
    v-bind="expansionTanks['1040-01']"
  />
  <TagLabelInstance
    :target-x="1215"
    :target-width="36"
    y="220"
    tag-id="1040-01"
  />
  <ExpansionValveInstance
    x="1145"
    y="145"
    v-bind="expansionValves['1041-01']"
  />
  <TagLabelInstance
    x="1165"
    y="145"
    tag-id="1041-01"
  />
</template>
