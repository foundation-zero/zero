<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
import { ManualValveType } from "../../../components/manual-valve";
import { ManualValveInstance } from "../../../instances";
import { PVT_MIMIC_DATA } from "../data";

const manualValves = PVT_MIMIC_DATA[MimicComponentType.ManualValve];
</script>

<template>
  <g>
    <ManualValveInstance
      x="988"
      y="418"
      tag-id="1170-05"
      :type="ManualValveType.Switch"
      :orientation="ComponentOrientation.Up"
      v-bind="manualValves['1170-05']"
    />
    <ManualValveInstance
      x="988"
      y="483"
      tag-id="1170-06"
      :type="ManualValveType.Switch"
      :orientation="ComponentOrientation.Up"
      v-bind="manualValves['1170-06']"
    />
    <ManualValveInstance
      x="879"
      y="595"
      tag-id="1177-01"
      :type="ManualValveType.Switch"
      :orientation="ComponentOrientation.Right"
      v-bind="manualValves['1177-01']"
    />
    <ManualValveInstance
      x="950"
      y="595"
      tag-id="1177-02"
      :type="ManualValveType.Switch"
      :orientation="ComponentOrientation.Right"
      v-bind="manualValves['1177-02']"
    />
  </g>
</template>
