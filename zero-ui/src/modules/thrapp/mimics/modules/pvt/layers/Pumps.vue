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
      x="528"
      y="193.3"
      :orientation="ComponentOrientation.Left"
      v-bind="pumps['1018']"
    >
      <DutypointLabelInstance
        :target-x="530"
        :target-width="PUMP_WIDTH"
        y="163.5"
        :tag-id="pumps['1018'].tooltip?.yardTag"
        :pump="pumps['1018'].controls.pump"
      />
    </PumpInstance>
    <PumpInstance
      x="528"
      y="389.92"
      :orientation="ComponentOrientation.Left"
      v-bind="pumps['1019']"
    >
      <DutypointLabelInstance
        :target-x="530"
        :target-width="PUMP_WIDTH"
        y="363.5"
        :tag-id="pumps['1019'].tooltip?.yardTag"
        :pump="pumps['1019'].controls.pump"
      />
    </PumpInstance>
    <PumpInstance
      x="528"
      y="613.15"
      :orientation="ComponentOrientation.Left"
      v-bind="pumps['1021']"
    >
      <DutypointLabelInstance
        :target-x="530"
        :target-width="PUMP_WIDTH"
        y="585.5"
        :tag-id="pumps['1021'].tooltip?.yardTag"
        :pump="pumps['1021'].controls.pump"
      />
    </PumpInstance>
    <ManualPumpInstance
      x="885"
      y="519"
      :width="28"
      :height="28"
      :orientation="ComponentOrientation.Left"
      v-bind="manualPumps['1182']"
    >
      <TagLabelInstance
        :target-x="885"
        :target-width="28"
        y="550"
        :tag-id="manualPumps['1182'].tooltip?.yardTag"
      />
    </ManualPumpInstance>
  </g>
</template>
