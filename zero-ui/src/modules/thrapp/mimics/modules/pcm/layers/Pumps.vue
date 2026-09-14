<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
import { DutypointLabelInstance, PumpInstance } from "../../../instances";
import { PCM_MIMIC_DATA } from "../data";

const pumps = PCM_MIMIC_DATA[MimicComponentType.Pump];
</script>

<template>
  <g>
    <PumpInstance
      x="313"
      y="670"
      :width="32"
      :height="32"
      :orientation="ComponentOrientation.Up"
      v-bind="pumps['1017']"
    >
      <DutypointLabelInstance
        target-x="270"
        :target-width="32"
        y="670"
        :tag-id="pumps['1017'].tooltip?.yardTag"
        :pump="pumps['1017'].controls.pump"
      />
    </PumpInstance>
  </g>
</template>
