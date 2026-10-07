<script setup lang="ts">
import { ComponentOrientation } from "../../../components";
import { CHECK_VALVE_WIDTH } from "../../../components/check-valve";
import { CheckValveInstance, TagLabelInstance } from "../../../instances";
import { DRIVES_CHECK_VALVE_DATA } from "../data";

const checkValves = DRIVES_CHECK_VALVE_DATA.CheckValve;
</script>

<template>
  <g>
    <CheckValveInstance
      x="1302"
      y="592.916"
      :orientation="ComponentOrientation.Left"
      v-bind="checkValves['1090-01']"
    >
      <TagLabelInstance
        target-x="1302"
        :target-width="CHECK_VALVE_WIDTH"
        y="628.7832"
        :tag-id="checkValves['1090-01'].tooltip?.yardTag"
      />
    </CheckValveInstance>
    <CheckValveInstance
      x="1302.0018"
      y="726"
      :orientation="ComponentOrientation.Left"
      v-bind="checkValves['1090-02']"
    >
      <TagLabelInstance
        target-x="1302.0018"
        :target-width="CHECK_VALVE_WIDTH"
        y="762.6006"
        :tag-id="checkValves['1090-02'].tooltip?.yardTag"
      />
    </CheckValveInstance>
  </g>
</template>
