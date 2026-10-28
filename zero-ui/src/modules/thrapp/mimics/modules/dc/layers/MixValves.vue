<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
import { ACTUATED_VALVE_WIDTH, ValveLeg, ValvePortName } from "../../../components/actuated-valve";
import { getTooltipContexts } from "../../../data";
import { MixValveInstance, ThreeWayValveLabelInstance } from "../../../instances";

const mixValves = getTooltipContexts(MimicComponentType.MixValve, [
  "1043-02",
  "1042-03",
  "1045-01",
  "1046-04",
  "1046-05",
]);
</script>

<template>
  <MixValveInstance
    x="616"
    y="180.1458"
    :orientation="ComponentOrientation.Down"
    v-bind="mixValves['1043-02']"
  >
    <ThreeWayValveLabelInstance
      target-x="613"
      :target-width="ACTUATED_VALVE_WIDTH"
      y="219.646"
      :tag-id="mixValves['1043-02'].tooltip?.yardTag"
      :valve="mixValves['1043-02'].source"
    />
  </MixValveInstance>
  <MixValveInstance
    x="616"
    y="623.1458"
    :orientation="ComponentOrientation.Down"
    v-bind="mixValves['1042-03']"
  >
    <ThreeWayValveLabelInstance
      target-x="613"
      :target-width="ACTUATED_VALVE_WIDTH"
      y="664.646"
      :tag-id="mixValves['1042-03'].tooltip?.yardTag"
      :valve="mixValves['1042-03'].source"
    />
  </MixValveInstance>
  <MixValveInstance
    x="616"
    y="393.1458"
    :orientation="ComponentOrientation.Down"
    v-bind="mixValves['1045-01']"
  >
    <ThreeWayValveLabelInstance
      target-x="613"
      :target-width="ACTUATED_VALVE_WIDTH"
      y="433.646"
      :tag-id="mixValves['1045-01'].tooltip?.yardTag"
      :valve="mixValves['1045-01'].source"
    />
  </MixValveInstance>
  <MixValveInstance
    x="1087.1406"
    y="394.1458"
    :orientation="ComponentOrientation.Down"
    v-bind="mixValves['1046-04']"
  >
    <ThreeWayValveLabelInstance
      target-x="1087.1406"
      :target-width="ACTUATED_VALVE_WIDTH"
      y="436.646"
      :tag-id="mixValves['1046-04'].tooltip?.yardTag"
      :valve="mixValves['1046-04'].source"
    />
  </MixValveInstance>
  <MixValveInstance
    x="820.1406"
    y="393.1458"
    :orientation="ComponentOrientation.Up"
    :legs="{
      [ValveLeg.Left]: ValvePortName.AB,
      [ValveLeg.Right]: ValvePortName.A,
      [ValveLeg.Bottom]: ValvePortName.B,
    }"
    v-bind="mixValves['1046-05']"
  >
    <ThreeWayValveLabelInstance
      x="816.1406"
      y="349.646"
      :tag-id="mixValves['1046-05'].tooltip?.yardTag"
      :valve="mixValves['1046-05'].source"
    />
  </MixValveInstance>
</template>
