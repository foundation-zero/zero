<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types/index.ts";
import BoilerTankInstance from "../../../instances/BoilerTankInstance.vue";
import { DHW_MIMIC_DATA } from "../data/index.ts";

const boilerTanks = DHW_MIMIC_DATA[MimicComponentType.BoilerTank];
</script>

<template>
  <BoilerTankInstance
    x="355"
    y="0"
    force-height
    v-bind="boilerTanks['1053']"
  />

  <BoilerTankInstance
    x="718"
    y="0"
    force-height
    v-bind="boilerTanks['1054']"
  />

  <BoilerTankInstance
    x="1056"
    y="0"
    force-height
    v-bind="boilerTanks['1055']"
  />
</template>
