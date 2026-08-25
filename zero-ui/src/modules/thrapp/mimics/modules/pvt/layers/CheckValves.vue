<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
import { CheckValveInstance } from "../../../instances";
import TagLabelInstance from "../../../instances/TagLabelInstance.vue";
import { PVT_MIMIC_DATA } from "../data";

const checkValves = PVT_MIMIC_DATA[MimicComponentType.CheckValve];
</script>

<template>
  <g>
    <CheckValveInstance
      x="430"
      y="200"
      :orientation="ComponentOrientation.Left"
      v-bind="checkValves['1188-01']"
    >
      <TagLabelInstance
        x="430"
        y="234"
        :tag-id="checkValves['1188-01'].tooltip?.yardTag"
      />
    </CheckValveInstance>
    <CheckValveInstance
      x="430"
      y="400"
      :orientation="ComponentOrientation.Left"
      v-bind="checkValves['1188-02']"
    >
      <TagLabelInstance
        x="430"
        y="434"
        :tag-id="checkValves['1188-02'].tooltip?.yardTag"
      />
    </CheckValveInstance>
    <CheckValveInstance
      x="430"
      y="620"
      :orientation="ComponentOrientation.Left"
      v-bind="checkValves['1188-03']"
    >
      <TagLabelInstance
        x="430"
        y="654"
        :tag-id="checkValves['1188-03'].tooltip?.yardTag"
      />
    </CheckValveInstance>
    <CheckValveInstance
      x="750"
      y="104"
      :orientation="ComponentOrientation.Right"
      v-bind="checkValves['1077-01']"
    >
      <TagLabelInstance
        x="750"
        y="128"
        :tag-id="checkValves['1077-01'].tooltip?.yardTag"
      />
    </CheckValveInstance>
    <CheckValveInstance
      x="750"
      y="312"
      :orientation="ComponentOrientation.Right"
      v-bind="checkValves['1077-02']"
    >
      <TagLabelInstance
        x="750"
        y="335"
        :tag-id="checkValves['1077-02'].tooltip?.yardTag"
      />
    </CheckValveInstance>
    <CheckValveInstance
      x="750"
      y="520"
      :orientation="ComponentOrientation.Right"
      v-bind="checkValves['1076-01']"
    >
      <TagLabelInstance
        x="750"
        y="543"
        :tag-id="checkValves['1076-01'].tooltip?.yardTag"
      />
    </CheckValveInstance>
    <CheckValveInstance
      x="885"
      y="622"
      :orientation="ComponentOrientation.Left"
      v-bind="checkValves['1085-01']"
    >
      <TagLabelInstance
        x="885"
        y="653"
        :tag-id="checkValves['1085-01'].tooltip?.yardTag"
      />
    </CheckValveInstance>
  </g>
</template>
