<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { getTooltipContexts } from "../../../data";
import {
  ExpansionTankInstance,
  ExpansionValveInstance,
  TagLabelInstance,
} from "../../../instances";

const expansionTanks = getTooltipContexts(MimicComponentType.ExpansionTank, ["1092"]);
const expansionValves = getTooltipContexts(MimicComponentType.ExpansionValve, ["1041-04"]);
</script>

<template>
  <ExpansionTankInstance
    x="1108"
    y="127"
    v-bind="expansionTanks['1092']"
  />

  <ExpansionValveInstance
    x="1050"
    y="108"
    v-bind="expansionValves['1041-04']"
  />
  <TagLabelInstance
    :target-x="1050"
    :target-width="36"
    y="92"
    tag-id="1041-04"
  />
  <TagLabelInstance
    x="1152"
    y="146"
    tag-id="1092"
  />
</template>
