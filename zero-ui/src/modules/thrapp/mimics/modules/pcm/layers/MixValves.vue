<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
import { ACTUATED_VALVE_WIDTH, ValveLeg, ValvePortName } from "../../../components/actuated-valve";
import { getTooltipContexts } from "../../../data";
import { MixValveInstance, ThreeWayValveLabelInstance } from "../../../instances";

const mixValves = getTooltipContexts(MimicComponentType.MixValve, ["25001135"]);
</script>

<template>
  <g>
    <MixValveInstance
      x="1292.4"
      y="108.7"
      :orientation="ComponentOrientation.Up"
      :legs="{
        [ValveLeg.Left]: ValvePortName.B,
        [ValveLeg.Right]: ValvePortName.AB,
        [ValveLeg.Bottom]: ValvePortName.A,
      }"
      v-bind="mixValves['25001135']"
    >
      <ThreeWayValveLabelInstance
        target-x="1292.4"
        :target-width="ACTUATED_VALVE_WIDTH"
        y="74.7"
        :tag-id="mixValves['25001135'].tooltip?.yardTag"
        :valve="mixValves['25001135'].source"
      />
    </MixValveInstance>
  </g>
</template>
