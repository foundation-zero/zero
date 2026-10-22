<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { getTooltipContexts } from "../../../data";
import {
  ExpansionTankInstance,
  ExpansionValveInstance,
  TagLabelInstance,
} from "../../../instances";

const expansionTanks = getTooltipContexts(MimicComponentType.ExpansionTank, ["1040-05"]);
const expansionValves = getTooltipContexts(MimicComponentType.ExpansionValve, ["1041-06"]);
</script>

<template>
  <ExpansionTankInstance
    x="1209.1406"
    y="619.1458"
    v-bind="expansionTanks['1040-05']"
  />
  <TagLabelInstance
    x="1247.1406"
    y="634.1458"
    tag-id="1040-05"
  />
  <ExpansionValveInstance
    x="1175.1406"
    y="675.6458"
    v-bind="expansionValves['1041-06']"
  />
  <TagLabelInstance
    x="1216.1406"
    y="677.1458"
    tag-id="1041-06"
  />
</template>
