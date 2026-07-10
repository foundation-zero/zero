<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
import { PumpInstance } from "../../../instances";
import { PVT_MIMIC_DATA } from "../data";

const pumps = PVT_MIMIC_DATA[MimicComponentType.Pump];
</script>

<template>
  <g>
    <PumpInstance
      x="965"
      y="542"
      :orientation="ComponentOrientation.Right"
      v-bind="pumps['1182']"
    />
  </g>
</template>
