<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
import { CheckValveInstance, TagLabelInstance } from "../../../instances";
import { DC_CHECK_VALVE_DATA } from "../data";

const checkValves = DC_CHECK_VALVE_DATA[MimicComponentType.CheckValve];
</script>

<template>
  <CheckValveInstance
    x="338"
    y="183.1458"
    :orientation="ComponentOrientation.Left"
    v-bind="checkValves['1076-03']"
  >
    <TagLabelInstance
      x="335"
      y="217.1458"
      :tag-id="checkValves['1076-03'].tooltip?.yardTag"
    />
  </CheckValveInstance>
  <CheckValveInstance
    x="338"
    y="395.1458"
    :orientation="ComponentOrientation.Left"
    v-bind="checkValves['1077-04']"
  >
    <TagLabelInstance
      x="335"
      y="429.1458"
      :tag-id="checkValves['1077-04'].tooltip?.yardTag"
    />
  </CheckValveInstance>
  <CheckValveInstance
    x="338"
    y="627.1458"
    :orientation="ComponentOrientation.Left"
    v-bind="checkValves['1075-01']"
  >
    <TagLabelInstance
      x="335"
      y="661.1458"
      :tag-id="checkValves['1075-01'].tooltip?.yardTag"
    />
  </CheckValveInstance>
  <CheckValveInstance
    x="757"
    y="88.1458"
    :orientation="ComponentOrientation.Right"
    v-bind="checkValves['1076-02']"
  >
    <TagLabelInstance
      x="754"
      y="112.1458"
      :tag-id="checkValves['1076-02'].tooltip?.yardTag"
    />
  </CheckValveInstance>
  <CheckValveInstance
    x="757"
    y="302.1458"
    :orientation="ComponentOrientation.Right"
    v-bind="checkValves['1077-03']"
  >
    <TagLabelInstance
      x="754"
      y="326.1458"
      :tag-id="checkValves['1077-03'].tooltip?.yardTag"
    />
  </CheckValveInstance>
  <CheckValveInstance
    x="757"
    y="533.1458"
    :orientation="ComponentOrientation.Right"
    v-bind="checkValves['1075-06']"
  >
    <TagLabelInstance
      x="754"
      y="557.1458"
      :tag-id="checkValves['1075-06'].tooltip?.yardTag"
    />
  </CheckValveInstance>
</template>
