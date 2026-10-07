<script setup lang="ts">
import { ComponentOrientation } from "../../../components";
import { ACTUATED_VALVE_WIDTH, ValveLeg, ValvePortName } from "../../../components/actuated-valve";
import { MixValveInstance, ThreeWayValveLabelInstance } from "../../../instances";
import { DRIVES_MIX_VALVE_DATA } from "../data";

const mixValves = DRIVES_MIX_VALVE_DATA.MixValve;
</script>

<template>
  <g>
    <MixValveInstance
      x="1039"
      y="594"
      :orientation="ComponentOrientation.Up"
      :legs="{
        [ValveLeg.Left]: ValvePortName.AB,
        [ValveLeg.Right]: ValvePortName.A,
        [ValveLeg.Bottom]: ValvePortName.B,
      }"
      v-bind="mixValves['1046-01']"
    >
      <ThreeWayValveLabelInstance
        target-x="1039"
        :target-width="ACTUATED_VALVE_WIDTH"
        y="559.916"
        :tag-id="mixValves['1046-01'].tooltip?.yardTag"
        :valve="mixValves['1046-01'].source"
      />
    </MixValveInstance>
    <MixValveInstance
      x="1649.1934"
      y="446.9512"
      :orientation="ComponentOrientation.Right"
      :legs="{
        [ValveLeg.Left]: ValvePortName.A,
        [ValveLeg.Right]: ValvePortName.AB,
        [ValveLeg.Bottom]: ValvePortName.B,
      }"
      v-bind="mixValves['1046-03']"
    >
      <ThreeWayValveLabelInstance
        x="1600.1582"
        y="419.916"
        :tag-id="mixValves['1046-03'].tooltip?.yardTag"
        :valve="mixValves['1046-03'].source"
      />
    </MixValveInstance>
  </g>
</template>
