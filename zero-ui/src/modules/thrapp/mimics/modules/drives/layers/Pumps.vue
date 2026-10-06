<script setup lang="ts">
import { ComponentOrientation } from "../../../components";
import { PUMP_WIDTH } from "../../../components/pump";
import { DutypointLabelInstance, PumpInstance } from "../../../instances";
import { DRIVES_PUMP_DATA } from "../data";

const pumps = DRIVES_PUMP_DATA.Pump;
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
        :height="33"
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
        :height="33"
        :tag-id="pumps['1029'].tooltip?.yardTag"
        :pump="pumps['1029'].controls.pump"
      />
    </PumpInstance>
  </g>
</template>
