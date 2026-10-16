<script setup lang="ts">
import {
  ExpansionTankInstance,
  ExpansionValveInstance,
  TagLabelInstance,
} from "../../../instances";
import { DC_EXPANSION_TANK_DATA, DC_EXPANSION_VALVE_DATA } from "../data";
</script>

<template>
  <ExpansionTankInstance
    x="1209.1406"
    y="619.1458"
    v-bind="DC_EXPANSION_TANK_DATA.ExpansionTank['1040-05']"
  />
  <TagLabelInstance
    x="1247.1406"
    y="634.1458"
    tag-id="1040-05"
  />
  <ExpansionValveInstance
    x="1175.1406"
    y="675.6458"
    v-bind="DC_EXPANSION_VALVE_DATA.ExpansionValve['1041-06']"
  />
  <TagLabelInstance
    x="1216.1406"
    y="677.1458"
    tag-id="1041-06"
  />
</template>
