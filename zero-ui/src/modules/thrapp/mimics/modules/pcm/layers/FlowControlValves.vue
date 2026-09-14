<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ACTUATED_VALVE_WIDTH } from "../../../components/actuated-valve";
import { ComponentOrientation } from "../../../components/index.ts";
import FlowControlLabelInstance from "../../../instances/FlowControlLabelInstance.vue";
import { FlowControlValveInstance } from "../../../instances/index.ts";
import { PCM_MIMIC_DATA } from "../data/index.ts";

const valves = PCM_MIMIC_DATA[MimicComponentType.FlowControlValve];
</script>

<template>
  <FlowControlValveInstance
    x="552"
    y="71"
    :orientation="ComponentOrientation.Down"
    v-bind="valves['1064-04']"
  >
    <FlowControlLabelInstance
      target-x="552"
      :target-width="ACTUATED_VALVE_WIDTH"
      y="40"
      :tag-id="valves['1064-04'].tooltip?.yardTag"
      :valve="valves['1064-04'].source"
    />
  </FlowControlValveInstance>
  <FlowControlValveInstance
    x="552"
    y="221"
    :orientation="ComponentOrientation.Down"
    v-bind="valves['1064-05']"
  >
    <FlowControlLabelInstance
      :x="552"
      :target-width="ACTUATED_VALVE_WIDTH"
      y="250"
      :tag-id="valves['1064-05'].tooltip?.yardTag"
      :valve="valves['1064-05'].source"
    />
  </FlowControlValveInstance>
  <FlowControlValveInstance
    x="552"
    y="418"
    :orientation="ComponentOrientation.Down"
    v-bind="valves['1064-06']"
  >
    <FlowControlLabelInstance
      target-x="552"
      :target-width="ACTUATED_VALVE_WIDTH"
      y="455"
      :tag-id="valves['1064-06'].tooltip?.yardTag"
      :valve="valves['1064-06'].source"
    />
  </FlowControlValveInstance>
  <FlowControlValveInstance
    x="552"
    y="614"
    :orientation="ComponentOrientation.Down"
    v-bind="valves['1064-07']"
  >
    <FlowControlLabelInstance
      target-x="552"
      :target-width="ACTUATED_VALVE_WIDTH"
      y="655"
      :tag-id="valves['1064-07'].tooltip?.yardTag"
      :valve="valves['1064-07'].source"
    />
  </FlowControlValveInstance>
  <FlowControlValveInstance
    x="1117"
    y="798"
    :orientation="ComponentOrientation.Left"
    v-bind="valves['1065-01']"
  >
    <FlowControlLabelInstance
      target-x="1125"
      y="790"
      :tag-id="valves['1065-01'].tooltip?.yardTag"
      :valve="valves['1065-01'].source"
    />
  </FlowControlValveInstance>
  <FlowControlValveInstance
    x="1242"
    y="798"
    :orientation="ComponentOrientation.Left"
    v-bind="valves['1061']"
  >
    <FlowControlLabelInstance
      target-x="1250"
      y="790"
      :tag-id="valves['1061'].tooltip?.yardTag"
      :valve="valves['1061'].source"
    />
  </FlowControlValveInstance>
  <FlowControlValveInstance
    x="1365"
    y="798"
    :orientation="ComponentOrientation.Left"
    v-bind="valves['1062-01']"
  >
    <FlowControlLabelInstance
      target-x="1373"
      y="790"
      :tag-id="valves['1062-01'].tooltip?.yardTag"
      :valve="valves['1062-01'].source"
    />
  </FlowControlValveInstance>
</template>
