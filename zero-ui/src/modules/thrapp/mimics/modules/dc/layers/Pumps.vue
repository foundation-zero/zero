<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
import { PUMP_WIDTH } from "../../../components/pump";
import { DutypointLabelInstance, PumpInstance } from "../../../instances";
import { DC_PUMP_DATA } from "../data";

const pumps = DC_PUMP_DATA[MimicComponentType.Pump];
</script>

<template>
  <PumpInstance
    x="456.25"
    y="172.1458"
    :orientation="ComponentOrientation.Left"
    v-bind="pumps['1020']"
  >
    <DutypointLabelInstance
      target-x="456.25"
      :target-width="PUMP_WIDTH"
      y="139.1458"
      :tag-id="pumps['1020'].tooltip?.yardTag"
      :pump="pumps['1020'].controls.pump"
    />
  </PumpInstance>
  <PumpInstance
    x="456.25"
    y="384.1458"
    :orientation="ComponentOrientation.Left"
    v-bind="pumps['1023']"
  >
    <DutypointLabelInstance
      target-x="456.25"
      :target-width="PUMP_WIDTH"
      y="352.1458"
      :tag-id="pumps['1023'].tooltip?.yardTag"
      :pump="pumps['1023'].controls.pump"
    />
  </PumpInstance>
  <PumpInstance
    x="456.25"
    y="614.1458"
    :orientation="ComponentOrientation.Left"
    v-bind="pumps['1025']"
  >
    <DutypointLabelInstance
      target-x="456.25"
      :target-width="PUMP_WIDTH"
      y="582.1458"
      :tag-id="pumps['1025'].tooltip?.yardTag"
      :pump="pumps['1025'].controls.pump"
    />
  </PumpInstance>
</template>
