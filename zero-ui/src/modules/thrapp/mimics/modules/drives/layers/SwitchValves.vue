<script setup lang="ts">
import { ComponentOrientation } from "../../../components";
import { ACTUATED_VALVE_WIDTH } from "../../../components/actuated-valve";
import { SwitchValveInstance } from "../../../instances";
import TagLabelInstance from "../../../instances/TagLabelInstance.vue";
import { DRIVES_SWITCH_VALVE_DATA } from "../data";

const switchValves = DRIVES_SWITCH_VALVE_DATA.SwitchValve;
</script>

<template>
  <SwitchValveInstance
    x="255.1582"
    y="164.916"
    :orientation="ComponentOrientation.Up"
    v-bind="switchValves['1069-09']"
  >
    <TagLabelInstance
      target-x="255.1582"
      :target-width="ACTUATED_VALVE_WIDTH"
      y="198.916"
      :tag-id="switchValves['1069-09'].tooltip?.yardTag"
    />
  </SwitchValveInstance>
  <SwitchValveInstance
    x="255.1582"
    y="384.916"
    :orientation="ComponentOrientation.Up"
    v-bind="switchValves['1069-06']"
  >
    <TagLabelInstance
      target-x="255.1582"
      :target-width="ACTUATED_VALVE_WIDTH"
      y="426.0156"
      :tag-id="switchValves['1069-06'].tooltip?.yardTag"
    />
  </SwitchValveInstance>
  <SwitchValveInstance
    x="256"
    y="617.916"
    :orientation="ComponentOrientation.Up"
    v-bind="switchValves['1069-08']"
  >
    <TagLabelInstance
      target-x="256"
      :target-width="ACTUATED_VALVE_WIDTH"
      y="650"
      :tag-id="switchValves['1069-08'].tooltip?.yardTag"
    />
  </SwitchValveInstance>
  <SwitchValveInstance
    x="256"
    y="825.916"
    :orientation="ComponentOrientation.Up"
    v-bind="switchValves['1069-07']"
  >
    <TagLabelInstance
      target-x="256"
      :target-width="ACTUATED_VALVE_WIDTH"
      y="861"
      :tag-id="switchValves['1069-07'].tooltip?.yardTag"
    />
  </SwitchValveInstance>
  <SwitchValveInstance
    x="923.1582"
    y="316.916"
    :orientation="ComponentOrientation.Right"
    v-bind="switchValves['1069-04']"
  >
    <TagLabelInstance
      x="880.6582"
      y="320"
      :tag-id="switchValves['1069-04'].tooltip?.yardTag"
    />
  </SwitchValveInstance>
  <SwitchValveInstance
    x="992.1582"
    y="315.916"
    :orientation="ComponentOrientation.Right"
    v-bind="switchValves['1069-05']"
  >
    <TagLabelInstance
      x="1037.6582"
      y="320"
      :tag-id="switchValves['1069-05'].tooltip?.yardTag"
    />
  </SwitchValveInstance>
</template>
