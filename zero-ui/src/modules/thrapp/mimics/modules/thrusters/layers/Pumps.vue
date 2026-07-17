<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
import { PumpInstance } from "../../../instances";
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
    />
    <PumpInstance
      x="696"
      y="604"
      :orientation="ComponentOrientation.Left"
      v-bind="pumps['1195']"
    />
  </g>
</template>
