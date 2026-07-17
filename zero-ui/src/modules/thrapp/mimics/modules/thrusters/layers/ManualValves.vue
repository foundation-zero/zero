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
      x="610"
      y="152"
      :type="ManualValveType.Switch"
      :orientation="ComponentOrientation.Up"
      v-bind="manualValves['1212-01']"
    />
    <ManualValveInstance
      x="732"
      y="152"
      :type="ManualValveType.Switch"
      :orientation="ComponentOrientation.Up"
      v-bind="manualValves['1212-02']"
    />
    <ManualValveInstance
      x="615.042"
      y="522"
      :type="ManualValveType.Switch"
      :orientation="ComponentOrientation.Up"
      v-bind="manualValves['1212-03']"
    />
    <ManualValveInstance
      x="744.057"
      y="522"
      :type="ManualValveType.Switch"
      :orientation="ComponentOrientation.Up"
      v-bind="manualValves['1212-04']"
    />
    <ManualValveInstance
      x="615.042"
      y="613"
      :type="ManualValveType.Switch"
      :orientation="ComponentOrientation.Up"
      v-bind="manualValves['1212-05']"
    />
    <ManualValveInstance
      x="742.224"
      y="613"
      :type="ManualValveType.Switch"
      :orientation="ComponentOrientation.Up"
      v-bind="manualValves['1212-06']"
    />
    <ManualValveInstance
      x="214"
      y="299"
      :type="ManualValveType.Switch"
      :orientation="ComponentOrientation.Up"
      v-bind="manualValves['1212-07']"
    />
    <ManualValveInstance
      x="1025.775"
      y="190.5"
      :type="ManualValveType.Switch"
      :orientation="ComponentOrientation.Up"
      v-bind="manualValves['1084-01']"
    />
    <ManualValveInstance
      x="214"
      y="567"
      :type="ManualValveType.Switch"
      :orientation="ComponentOrientation.Up"
      v-bind="manualValves['1087-03']"
    />
    <ManualValveInstance
      x="1025.775"
      y="140.5"
      :type="ManualValveType.Switch"
      :orientation="ComponentOrientation.Up"
      v-bind="manualValves['1087-08']"
    />
  </g>
</template>
