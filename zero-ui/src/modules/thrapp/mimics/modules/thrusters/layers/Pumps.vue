<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
import { PUMP_WIDTH } from "../../../components/pump";
import { DutypointLabelInstance, PumpInstance } from "../../../instances";
import { THRUSTERS_MIMIC_DATA } from "../data";

const pumps = THRUSTERS_MIMIC_DATA[MimicComponentType.Pump];
</script>

<template>
  <g>
    <PumpInstance
      x="686"
      y="513"
      :orientation="ComponentOrientation.Left"
      v-bind="pumps['1194']"
    >
      <DutypointLabelInstance
        :target-x="686"
        :target-width="PUMP_WIDTH"
        y="480"
        :tag-id="pumps['1194'].tooltip?.yardTag"
        :pump="pumps['1194'].controls.pump"
      />
    </PumpInstance>
    <PumpInstance
      x="686"
      y="604"
      :orientation="ComponentOrientation.Left"
      v-bind="pumps['1195']"
    >
      <DutypointLabelInstance
        :target-x="686"
        :target-width="PUMP_WIDTH"
        y="570"
        :tag-id="pumps['1195'].tooltip?.yardTag"
        :pump="pumps['1195'].controls.pump"
      />
    </PumpInstance>
  </g>
</template>
