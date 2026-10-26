<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
import { PUMP_WIDTH } from "../../../components/pump";
import { getTooltipContexts } from "../../../data";
import {
  DutypointLabelInstance,
  ManualPumpInstance,
  PumpInstance,
  TagLabelInstance,
} from "../../../instances";

const pumps = getTooltipContexts(MimicComponentType.Pump, ["1018", "1019", "1021"]);
const manualPumps = getTooltipContexts(MimicComponentType.ManualPump, ["1182"]);
</script>

<template>
  <g>
    <PumpInstance
      x="530"
      y="194"
      :orientation="ComponentOrientation.Left"
      v-bind="pumps['1018']"
    >
      <DutypointLabelInstance
        :target-x="530"
        :target-width="PUMP_WIDTH"
        y="161"
        :tag-id="pumps['1018'].tooltip?.yardTag"
        :pump="pumps['1018'].controls.pump"
      />
    </PumpInstance>
    <PumpInstance
      x="530"
      y="390"
      :orientation="ComponentOrientation.Left"
      v-bind="pumps['1019']"
    >
      <DutypointLabelInstance
        :target-x="530"
        :target-width="PUMP_WIDTH"
        y="356"
        :tag-id="pumps['1019'].tooltip?.yardTag"
        :pump="pumps['1019'].controls.pump"
      />
    </PumpInstance>
    <PumpInstance
      x="530"
      y="613"
      :orientation="ComponentOrientation.Left"
      v-bind="pumps['1021']"
    >
      <DutypointLabelInstance
        :target-x="530"
        :target-width="PUMP_WIDTH"
        y="580"
        :tag-id="pumps['1021'].tooltip?.yardTag"
        :pump="pumps['1021'].controls.pump"
      />
    </PumpInstance>
    <ManualPumpInstance
      x="872"
      y="506"
      :orientation="ComponentOrientation.Left"
      v-bind="manualPumps['1182']"
    >
      <TagLabelInstance
        :target-x="872"
        :target-width="PUMP_WIDTH"
        y="557"
        :tag-id="manualPumps['1182'].tooltip?.yardTag"
      />
    </ManualPumpInstance>
  </g>
</template>
