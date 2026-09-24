<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import ThrusterInstance from "../../../instances/ThrusterInstance.vue";
import { THRUSTERS_MIMIC_DATA } from "../data";

const thrusters = THRUSTERS_MIMIC_DATA[MimicComponentType.Thruster];
</script>

<template>
  <g>
    <ThrusterInstance
      x="23"
      y="143"
      v-bind="thrusters['9002-01']"
    />

    <ThrusterInstance
      x="23"
      y="401"
      v-bind="thrusters['9001-01']"
    />
  </g>
</template>
