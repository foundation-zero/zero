<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
import { DutypointLabelInstance, PumpInstance } from "../../../instances";
import { THRUSTERS_MIMIC_DATA } from "../data";

const pumps = THRUSTERS_MIMIC_DATA[MimicComponentType.Pump];
</script>

<template>
  <g>
    <PumpInstance
      x="696"
      y="513"
      :orientation="ComponentOrientation.Left"
      v-bind="pumps['1194']"
    >
      <DutypointLabelInstance
        x="706"
        y="480"
        tag-id="1194"
        :pump="pumps['1194'].source"
      />
    </PumpInstance>
    <PumpInstance
      x="696"
      y="604"
      :orientation="ComponentOrientation.Left"
      v-bind="pumps['1195']"
    >
      <DutypointLabelInstance
        x="706"
        y="570"
        tag-id="1195"
        :pump="pumps['1195'].source"
      />
    </PumpInstance>
  </g>
</template>
