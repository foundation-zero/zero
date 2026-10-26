<script setup lang="ts">
import { MimicComponentType } from "../../../../types";
import { ComponentOrientation } from "../../../components";
import { getTooltipContexts } from "../../../data";
import { DutypointLabelInstance, PumpInstance } from "../../../instances";

const pumps = getTooltipContexts(MimicComponentType.Pump, ["1022"]);
</script>

<template>
  <PumpInstance
    x="169.5"
    y="316"
    v-bind="pumps['1022']"
    :orientation="ComponentOrientation.Down"
  >
    <DutypointLabelInstance
      x="220"
      y="322"
      :tag-id="pumps['1022'].tooltip?.yardTag"
      :pump="pumps['1022'].controls.pump"
    />
  </PumpInstance>
</template>
