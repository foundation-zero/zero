<script setup lang="ts">
import {
  ExpansionTankInstance,
  ExpansionValveInstance,
  TagLabelInstance,
} from "../../../instances";
import { PVT_EXPANSION_TANK_DATA, PVT_EXPANSION_VALVE_DATA } from "../data";
</script>

<template>
  <ExpansionTankInstance
    x="1215"
    y="165"
    v-bind="PVT_EXPANSION_TANK_DATA.ExpansionTank['1040-01']"
  />
  <TagLabelInstance
    :target-x="1215"
    :target-width="36"
    y="220"
    tag-id="1040-01"
  />
  <ExpansionValveInstance
    x="1145"
    y="145"
    v-bind="PVT_EXPANSION_VALVE_DATA.ExpansionValve['1041-01']"
  />
  <TagLabelInstance
    x="1165"
    y="145"
    tag-id="1041-01"
  />
</template>
