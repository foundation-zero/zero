<script setup lang="ts">
import {
  ExpansionTankInstance,
  ExpansionValveInstance,
  TagLabelInstance,
} from "../../../instances";
import { DRIVES_EXPANSION_TANK_DATA, DRIVES_EXPANSION_VALVE_DATA } from "../data";
</script>

<template>
  <g>
    <ExpansionTankInstance
      x="1612"
      y="102"
      v-bind="DRIVES_EXPANSION_TANK_DATA.ExpansionTank['1040-04']"
    />
    <TagLabelInstance
      x="1568"
      y="118"
      tag-id="1040-04"
    />
    <g transform="matrix(0 1 1 0 1657 71)">
      <ExpansionValveInstance v-bind="DRIVES_EXPANSION_VALVE_DATA.ExpansionValve['1041-05']" />
    </g>
    <TagLabelInstance
      x="1607"
      y="69"
      tag-id="1041-05"
    />
  </g>
</template>
