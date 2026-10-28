<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
import { PUMP_WIDTH } from "../../../components/pump";
import { getTooltipContexts } from "../../../data";
import { DutypointLabelInstance, PumpInstance } from "../../../instances";

const pumps = getTooltipContexts(MimicComponentType.Pump, ["1020", "1023", "1025"]);
</script>

<template>
  <PumpInstance
    x="456.25"
    y="172.1458"
    :orientation="ComponentOrientation.Left"
    v-bind="pumps['1020']"
  >
    <DutypointLabelInstance
      target-x="458.25"
      :target-width="PUMP_WIDTH"
      y="141.646"
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
      target-x="458.25"
      :target-width="PUMP_WIDTH"
      y="354.646"
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
      target-x="458.25"
      :target-width="PUMP_WIDTH"
      y="584.646"
      :tag-id="pumps['1025'].tooltip?.yardTag"
      :pump="pumps['1025'].controls.pump"
    />
  </PumpInstance>
</template>
