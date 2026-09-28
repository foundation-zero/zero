<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
import { PUMP_WIDTH } from "../../../components/pump";
import { DutypointLabelInstance, PumpInstance } from "../../../instances";
import { PCM_MIMIC_DATA } from "../data";

const pumps = PCM_MIMIC_DATA[MimicComponentType.Pump];
</script>

<template>
  <g>
    <PumpInstance
      x="301"
      y="663"
      :orientation="ComponentOrientation.Up"
      v-bind="pumps['1017']"
    >
      <DutypointLabelInstance
        target-x="301"
        :target-width="-PUMP_WIDTH"
        y="673"
        :tag-id="pumps['1017'].tooltip?.yardTag"
        :pump="pumps['1017'].controls.pump"
      />
    </PumpInstance>
  </g>
</template>
