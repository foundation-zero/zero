<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { getTooltipContexts } from "../../../data";
import BoilerTankInstance from "../../../instances/BoilerTankInstance.vue";

const boilerTanks = getTooltipContexts(MimicComponentType.BoilerTank, ["1053", "1054", "1055"]);
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
