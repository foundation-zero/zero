<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { getTooltipContexts } from "../../../data";
import {
  ExpansionTankInstance,
  ExpansionValveInstance,
  TagLabelInstance,
} from "../../../instances";

const expansionTanks = getTooltipContexts(MimicComponentType.ExpansionTank, ["1040-03", "1040-02"]);
const expansionValves = getTooltipContexts(MimicComponentType.ExpansionValve, [
  "1041-03",
  "1041-02",
]);
</script>

<template>
  <g>
    <ExpansionTankInstance
      x="78"
      y="568"
      v-bind="expansionTanks['1040-03']"
    >
      <TagLabelInstance
        x="33"
        y="580"
        :tag-id="expansionTanks['1040-03'].tooltip?.yardTag"
      />
    </ExpansionTankInstance>
    <ExpansionTankInstance
      x="1737"
      y="579"
      v-bind="expansionTanks['1040-02']"
    >
      <TagLabelInstance
        x="1781"
        y="595"
        :tag-id="expansionTanks['1040-02'].tooltip?.yardTag"
      />
    </ExpansionTankInstance>
    <ExpansionValveInstance
      x="117"
      y="642.5"
      v-bind="expansionValves['1041-03']"
    >
      <TagLabelInstance
        x="68.5"
        y="639"
        :tag-id="expansionValves['1041-03'].tooltip?.yardTag"
      />
    </ExpansionValveInstance>
    <ExpansionValveInstance
      x="1691"
      y="545"
      v-bind="expansionValves['1041-02']"
    >
      <TagLabelInstance
        x="1730.5"
        y="543"
        :tag-id="expansionValves['1041-02'].tooltip?.yardTag"
      />
    </ExpansionValveInstance>
  </g>
</template>
