<script setup lang="ts">
import { ComponentOrientation } from "../../../components";
import { CheckValveInstance } from "../../../instances";
</script>

<template>
  <g>
    <CheckValveInstance
      x="255"
      y="149"
      tag-id="1169-05"
      :orientation="ComponentOrientation.Right"
    />
    <CheckValveInstance
      x="255"
      y="332"
      tag-id="1169-04"
      :orientation="ComponentOrientation.Right"
    />
    <CheckValveInstance
      x="255"
      y="543"
      tag-id="1168-12"
      :orientation="ComponentOrientation.Right"
    />

    <CheckValveInstance
      x="573"
      y="225"
      tag-id="1069-06"
      :orientation="ComponentOrientation.Right"
    />
    <CheckValveInstance
      x="679"
      y="225"
      tag-id="1169-07"
      :orientation="ComponentOrientation.Right"
    />

    <CheckValveInstance
      x="573"
      y="367"
      tag-id="1169-08"
      :orientation="ComponentOrientation.Right"
    />
    <CheckValveInstance
      x="679"
      y="367"
      tag-id="1169-09"
      :orientation="ComponentOrientation.Right"
    />

    <CheckValveInstance
      x="573"
      y="565"
      tag-id="1191-01"
      :orientation="ComponentOrientation.Right"
    />
    <CheckValveInstance
      x="679"
      y="565"
      tag-id="1191-02"
      :orientation="ComponentOrientation.Right"
    />

    <CheckValveInstance
      x="824"
      y="150"
      tag-id="1077-01"
      :orientation="ComponentOrientation.Right"
    />
    <CheckValveInstance
      x="824"
      y="366"
      tag-id="1077-02"
      :orientation="ComponentOrientation.Right"
    />
    <CheckValveInstance
      x="824"
      y="565"
      tag-id="1076-01"
      :orientation="ComponentOrientation.Right"
    />

    <CheckValveInstance
      x="1151"
      y="229"
      tag-id="1167-01"
      :orientation="ComponentOrientation.Left"
    />
    <CheckValveInstance
      x="1151"
      y="276"
      tag-id="1167-11"
      :orientation="ComponentOrientation.Left"
    />
  </g>
</template>
