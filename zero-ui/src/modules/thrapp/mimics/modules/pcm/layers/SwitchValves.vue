<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
import { SwitchValveInstance } from "../../../instances";
import TagLabelInstance from "../../../instances/TagLabelInstance.vue";
import { PCM_MIMIC_DATA } from "../data";

const valves = PCM_MIMIC_DATA[MimicComponentType.SwitchValve];
</script>

<template>
  <SwitchValveInstance
    x="362"
    y="17"
    :orientation="ComponentOrientation.Right"
    v-bind="valves['1190-01']"
  >
    <TagLabelInstance
      x="330"
      y="20"
      :tag-id="valves['1190-01'].tooltip?.yardTag"
    />
  </SwitchValveInstance>
  <SwitchValveInstance
    x="311"
    y="723"
    :orientation="ComponentOrientation.Right"
    v-bind="valves['1066-01']"
  >
    <TagLabelInstance
      x="274"
      y="725"
      :tag-id="valves['1066-01'].tooltip?.yardTag"
    />
  </SwitchValveInstance>
  <SwitchValveInstance
    x="388"
    y="808"
    :orientation="ComponentOrientation.Right"
    v-bind="valves['1062-02']"
  >
    <TagLabelInstance
      x="423"
      y="812"
      :tag-id="valves['1062-02'].tooltip?.yardTag"
    />
  </SwitchValveInstance>
  <SwitchValveInstance
    x="1243"
    y="390"
    :orientation="ComponentOrientation.Right"
    v-bind="valves['1066-02']"
  >
    <TagLabelInstance
      x="1205"
      y="395"
      :tag-id="valves['1066-02'].tooltip?.yardTag"
    />
  </SwitchValveInstance>
  <SwitchValveInstance
    x="1118.5"
    y="210"
    :orientation="ComponentOrientation.Right"
    v-bind="valves['1067-15']"
  >
    <TagLabelInstance
      x="1085"
      y="215"
      :tag-id="valves['1067-15'].tooltip?.yardTag"
    />
  </SwitchValveInstance>
  <SwitchValveInstance
    x="950"
    y="-15"
    :orientation="ComponentOrientation.Up"
    v-bind="valves['1071-02']"
  >
    <TagLabelInstance
      x="952"
      y="7"
      :tag-id="valves['1071-02'].tooltip?.yardTag"
    />
  </SwitchValveInstance>
</template>
