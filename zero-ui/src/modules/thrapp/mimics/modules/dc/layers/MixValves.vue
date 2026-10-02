<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
import { ACTUATED_VALVE_WIDTH, ValveLeg, ValvePortName } from "../../../components/actuated-valve";
import { MixValveInstance, ThreeWayValveLabelInstance } from "../../../instances";
import { DC_MIX_VALVE_DATA } from "../data";

const mixValves = DC_MIX_VALVE_DATA[MimicComponentType.MixValve];
</script>

<template>
  <MixValveInstance
    x="616"
    y="180.1458"
    :orientation="ComponentOrientation.Down"
    v-bind="mixValves['1043-02']"
  >
    <ThreeWayValveLabelInstance
      target-x="605"
      :target-width="ACTUATED_VALVE_WIDTH"
      y="212.1458"
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
      target-x="616"
      :target-width="ACTUATED_VALVE_WIDTH"
      y="662.1458"
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
      target-x="605"
      :target-width="ACTUATED_VALVE_WIDTH"
      y="431.1458"
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
      y="434.1458"
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
      y="356.1458"
      :tag-id="mixValves['1046-05'].tooltip?.yardTag"
      :valve="mixValves['1046-05'].source"
    />
  </MixValveInstance>
</template>
