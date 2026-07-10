<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
import { ManualValveType } from "../../../components/manual-valve";
import { ManualValveInstance } from "../../../instances";
import { THRUSTERS_MIMIC_DATA } from "../data";

const manualValves = THRUSTERS_MIMIC_DATA[MimicComponentType.ManualValve];
</script>

<template>
  <g>
    <ManualValveInstance
      x="214.179"
      y="241.626"
      :type="ManualValveType.Switch"
      :orientation="ComponentOrientation.Right"
      v-bind="manualValves['1212-07']"
    />
    <ManualValveInstance
      x="610"
      y="152"
      :type="ManualValveType.Switch"
      :orientation="ComponentOrientation.Up"
      v-bind="manualValves['1212-1']"
    />
    <ManualValveInstance
      x="732"
      y="152"
      :type="ManualValveType.Switch"
      :orientation="ComponentOrientation.Up"
      v-bind="manualValves['1212-2']"
    />
    <ManualValveInstance
      x="615.042"
      y="422.4"
      :type="ManualValveType.Switch"
      :orientation="ComponentOrientation.Right"
      v-bind="manualValves['1212-3']"
    />
    <ManualValveInstance
      x="744.057"
      y="421.608"
      :type="ManualValveType.Switch"
      :orientation="ComponentOrientation.Right"
      v-bind="manualValves['1212-4']"
    />
    <ManualValveInstance
      x="615.042"
      y="496.188"
      :type="ManualValveType.Switch"
      :orientation="ComponentOrientation.Right"
      v-bind="manualValves['1212-5']"
    />
    <ManualValveInstance
      x="742.224"
      y="497.046"
      :type="ManualValveType.Switch"
      :orientation="ComponentOrientation.Right"
      v-bind="manualValves['1212-6']"
    />
    <ManualValveInstance
      x="214.179"
      y="459.756"
      :type="ManualValveType.Switch"
      :orientation="ComponentOrientation.Right"
      v-bind="manualValves['1213-1']"
    />
    <ManualValveInstance
      x="1025.775"
      y="153.252"
      :type="ManualValveType.Switch"
      :orientation="ComponentOrientation.Right"
      v-bind="manualValves['1087-01']"
    />
    <ManualValveInstance
      x="1025.775"
      y="113.52"
      :type="ManualValveType.Switch"
      :orientation="ComponentOrientation.Right"
      v-bind="manualValves['1087-08']"
    />
  </g>
</template>
