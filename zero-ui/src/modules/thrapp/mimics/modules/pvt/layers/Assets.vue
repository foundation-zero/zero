<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { PvtInstance } from "../../../instances";
import { PVT_MIMIC_DATA } from "../data";

const pvt = PVT_MIMIC_DATA[MimicComponentType.Pvt];
</script>

<template>
  <g>
    <PvtInstance
      x="14"
      y="30"
      :tag-id="pvt['9001-01'].tooltip?.yardTag"
      v-bind="pvt['9001-01']"
    />

    <PvtInstance
      x="14"
      y="241"
      :tag-id="pvt['9002-01'].tooltip?.yardTag"
      v-bind="pvt['9002-01']"
    />

    <PvtInstance
      x="14"
      y="455"
      :tag-id="pvt['9001-03'].tooltip?.yardTag"
      v-bind="pvt['9001-03']"
    />
  </g>
</template>
