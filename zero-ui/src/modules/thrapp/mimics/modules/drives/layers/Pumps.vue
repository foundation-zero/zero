<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
import { PUMP_WIDTH } from "../../../components/pump";
import { getTooltipContexts } from "../../../data";
import { DutypointLabelInstance, PumpInstance } from "../../../instances";

const pumps = getTooltipContexts(MimicComponentType.Pump, ["1028", "1029"]);
</script>

<template>
  <g>
    <PumpInstance
      x="1411.8037"
      y="584.916"
      :orientation="ComponentOrientation.Left"
      v-bind="pumps['1028']"
    >
      <DutypointLabelInstance
        target-x="1411.8037"
        :target-width="PUMP_WIDTH"
        y="547.916"
        :tag-id="pumps['1028'].tooltip?.yardTag"
        :pump="pumps['1028'].controls.pump"
      />
    </PumpInstance>
    <PumpInstance
      x="1411.8037"
      y="717.7334"
      :orientation="ComponentOrientation.Left"
      v-bind="pumps['1029']"
    >
      <DutypointLabelInstance
        target-x="1411.8037"
        :target-width="PUMP_WIDTH"
        y="780.6006"
        :tag-id="pumps['1029'].tooltip?.yardTag"
        :pump="pumps['1029'].controls.pump"
      />
    </PumpInstance>
  </g>
</template>
