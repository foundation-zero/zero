<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { getTooltipContexts } from "../../../data";
import {
  ExpansionTankInstance,
  ExpansionValveInstance,
  TagLabelInstance,
} from "../../../instances";

const expansionTanks = getTooltipContexts(MimicComponentType.ExpansionTank, ["1040-01"]);
const expansionValves = getTooltipContexts(MimicComponentType.ExpansionValve, [
  "1041-01",
  "1039-01",
]);
</script>

<template>
  <ExpansionTankInstance
    x="1220"
    y="167"
    v-bind="expansionTanks['1040-01']"
  />
  <TagLabelInstance
    :target-x="1226"
    :target-width="36"
    y="224"
    tag-id="1040-01"
  />
  <ExpansionValveInstance
    x="1145"
    y="145"
    v-bind="expansionValves['1041-01']"
  />
  <TagLabelInstance
    x="1168"
    y="143"
    tag-id="1041-01"
  />
  <ExpansionValveInstance
    x="837.5"
    y="172"
    v-bind="expansionValves['1039-01']"
  />
  <TagLabelInstance
    x="828"
    y="197"
    tag-id="1039-01"
  />
</template>
