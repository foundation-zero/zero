<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
import {
  DutypointLabelInstance,
  ManualPumpInstance,
  PumpInstance,
  TagLabelInstance,
} from "../../../instances";
import { PVT_MIMIC_DATA } from "../data";

const pumps = PVT_MIMIC_DATA[MimicComponentType.Pump];
const manualPumps = PVT_MIMIC_DATA[MimicComponentType.ManualPump];
</script>

<template>
  <g>
    <PumpInstance
      x="542"
      y="205"
      :width="32"
      :height="32"
      :orientation="ComponentOrientation.Left"
      v-bind="pumps['1018']"
    >
      <DutypointLabelInstance
        :target-x="542"
        :target-width="32"
        y="170"
        :tag-id="pumps['1018'].tooltip?.yardTag"
        :pump="pumps['1018'].controls.pump"
      />
    </PumpInstance>
    <PumpInstance
      x="542"
      y="401"
      :width="32"
      :height="32"
      :orientation="ComponentOrientation.Left"
      v-bind="pumps['1019']"
    >
      <DutypointLabelInstance
        :target-x="542"
        :target-width="32"
        y="365"
        :tag-id="pumps['1019'].tooltip?.yardTag"
        :pump="pumps['1019'].controls.pump"
      />
    </PumpInstance>
    <PumpInstance
      x="542"
      y="624"
      :width="32"
      :height="32"
      :orientation="ComponentOrientation.Left"
      v-bind="pumps['1020']"
    >
      <DutypointLabelInstance
        :target-x="542"
        :target-width="32"
        y="590"
        :tag-id="pumps['1020'].tooltip?.yardTag"
        :pump="pumps['1020'].controls.pump"
      />
    </PumpInstance>
    <ManualPumpInstance
      x="882"
      y="516"
      :width="32"
      :height="32"
      :orientation="ComponentOrientation.Left"
      v-bind="manualPumps['1182']"
    >
      <TagLabelInstance
        :target-x="882"
        :target-width="32"
        y="547"
        :tag-id="manualPumps['1182'].tooltip?.yardTag"
      />
    </ManualPumpInstance>
  </g>
</template>
