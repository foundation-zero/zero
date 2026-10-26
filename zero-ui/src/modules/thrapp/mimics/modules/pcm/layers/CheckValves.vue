<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
import { getTooltipContexts } from "../../../data";
import { CheckValveInstance } from "../../../instances";
import TagLabelInstance from "../../../instances/TagLabelInstance.vue";

const checkValves = getTooltipContexts(MimicComponentType.CheckValve, ["1078-01", "1085-02"]);
</script>

<template>
  <g>
    <CheckValveInstance
      x="313"
      y="620"
      :orientation="ComponentOrientation.Up"
      v-bind="checkValves['1078-01']"
    >
      <TagLabelInstance
        target-x="290"
        y="620"
        :tag-id="checkValves['1078-01'].tooltip?.yardTag"
      />
    </CheckValveInstance>
    <CheckValveInstance
      x="1003"
      y="60"
      :orientation="ComponentOrientation.Up"
      v-bind="checkValves['1085-02']"
    >
      <TagLabelInstance
        target-x="980"
        y="60"
        :tag-id="checkValves['1085-02'].tooltip?.yardTag"
      />
    </CheckValveInstance>
  </g>
</template>
