<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
import { MANUAL_VALVE_WIDTH, ManualValveType } from "../../../components/manual-valve";
import { ManualValveInstance } from "../../../instances";
import TagLabelInstance from "../../../instances/TagLabelInstance.vue";
import { PCM_MIMIC_DATA } from "../data";

const manualValves = PCM_MIMIC_DATA[MimicComponentType.ManualValve];
</script>

<template>
  <g>
    <ManualValveInstance
      x="552"
      y="156"
      :type="ManualValveType.Switch"
      :orientation="ComponentOrientation.Up"
      v-bind="manualValves['1168-23']"
    >
      <TagLabelInstance
        x="552"
        y="140"
        :tag-id="manualValves['1168-23'].tooltip?.yardTag"
      />
    </ManualValveInstance>
    <ManualValveInstance
      x="552"
      y="366"
      :type="ManualValveType.Switch"
      :orientation="ComponentOrientation.Up"
      v-bind="manualValves['1168-24']"
    >
      <TagLabelInstance
        x="552"
        y="350"
        :tag-id="manualValves['1168-24'].tooltip?.yardTag"
      />
    </ManualValveInstance>
    <ManualValveInstance
      x="552"
      y="564"
      :type="ManualValveType.Switch"
      :orientation="ComponentOrientation.Up"
      v-bind="manualValves['1168-25']"
    >
      <TagLabelInstance
        x="552"
        y="546"
        :tag-id="manualValves['1168-25'].tooltip?.yardTag"
      />
    </ManualValveInstance>
    <ManualValveInstance
      x="552"
      y="760"
      :type="ManualValveType.Switch"
      :orientation="ComponentOrientation.Up"
      v-bind="manualValves['1168-26']"
    >
      <TagLabelInstance
        x="552"
        y="742"
        :tag-id="manualValves['1168-26'].tooltip?.yardTag"
      />
    </ManualValveInstance>
    <ManualValveInstance
      x="949"
      y="110"
      :type="ManualValveType.Switch"
      :orientation="ComponentOrientation.Up"
      v-bind="manualValves['1067-09']"
    >
      <TagLabelInstance
        x="949"
        y="96"
        :tag-id="manualValves['1067-09'].tooltip?.yardTag"
      />
    </ManualValveInstance>
    <ManualValveInstance
      x="949"
      y="169"
      :type="ManualValveType.Switch"
      :orientation="ComponentOrientation.Up"
      v-bind="manualValves['1067-10']"
    >
      <TagLabelInstance
        x="949"
        y="155"
        :tag-id="manualValves['1067-10'].tooltip?.yardTag"
      />
    </ManualValveInstance>
    <ManualValveInstance
      x="311"
      y="563"
      :type="ManualValveType.Switch"
      :orientation="ComponentOrientation.Right"
      v-bind="manualValves['??????']"
    >
      <TagLabelInstance
        x="285"
        :target-width="MANUAL_VALVE_WIDTH"
        y="565"
        :tag-id="manualValves['??????'].tooltip?.yardTag"
      />
    </ManualValveInstance>
  </g>
</template>
