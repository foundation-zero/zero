<script setup lang="ts">
import {
  ExpansionTankInstance,
  ExpansionValveInstance,
  TagLabelInstance,
} from "../../../instances";
import { THRUSTERS_EXPANSION_TANK_DATA, THRUSTERS_EXPANSION_VALVE_DATA } from "../data";
</script>

<template>
  <ExpansionTankInstance
    x="1108"
    y="135"
    v-bind="THRUSTERS_EXPANSION_TANK_DATA.ExpansionTank['1092']"
  />

  <ExpansionValveInstance
    x="1050"
    y="108"
    v-bind="THRUSTERS_EXPANSION_VALVE_DATA.ExpansionValve['1041-04']"
  />
  <TagLabelInstance
    :target-x="1050"
    :target-width="36"
    y="92"
    tag-id="1041-04"
  />
  <TagLabelInstance
    x="1144"
    y="152"
    tag-id="1092"
  />
</template>
