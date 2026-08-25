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
        x="543"
        y="160"
        :tag-id="pumps['1018'].tooltip?.yardTag"
        :pump="pumps['1018'].source"
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
        x="543"
        y="360"
        :tag-id="pumps['1019'].tooltip?.yardTag"
        :pump="pumps['1019'].source"
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
        x="543"
        y="580"
        :tag-id="pumps['1020'].tooltip?.yardTag"
        :pump="pumps['1020'].source"
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
        x="888"
        y="547"
        :tag-id="manualPumps['1182'].tooltip?.yardTag"
      />
    </ManualPumpInstance>
  </g>
</template>
