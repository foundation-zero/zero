<script setup lang="ts">
import { MimicComponentType } from "../../../../types";
import { ComponentOrientation } from "../../../components";
import { PumpInstance } from "../../../instances";
import FlowControlLabelInstance from "../../../instances/FlowControlLabelInstance.vue";
import { DHW_MIMIC_DATA } from "../data";

const pumps = DHW_MIMIC_DATA[MimicComponentType.Pump];
</script>

<template>
  <PumpInstance
    x="169.5"
    y="316"
    v-bind="pumps['1022']"
    :orientation="ComponentOrientation.Down"
  >
    <FlowControlLabelInstance
      x="220"
      y="329"
      tag-id="1022"
      :valve="pumps['1022'].source"
    />
  </PumpInstance>
</template>
