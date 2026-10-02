<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { DcConverterInstance } from "../../../instances";
import { DC_MIMIC_DATA } from "../data";

const converters = DC_MIMIC_DATA[MimicComponentType.DcConverter];
</script>

<template>
  <DcConverterInstance
    x="19"
    y="28"
    v-bind="converters.aft"
  />
  <DcConverterInstance
    x="19"
    y="260"
    v-bind="converters.ugrid"
  />
  <DcConverterInstance
    x="19"
    y="498"
    v-bind="converters.fwd"
  />
</template>
