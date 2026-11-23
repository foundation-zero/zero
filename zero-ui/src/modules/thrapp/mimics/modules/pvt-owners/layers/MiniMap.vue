<script setup lang="ts">
import { OwnersBiminiOutline } from "../../../components/bimini-outline";
import { toBiminiStringProps } from "../../../components/mini-map";
import { SolarPanelStringInstance } from "../../../instances";
import { OWNERS_BIMINI_STRINGS } from "../layout";

// The top-down view of the owners bimini, without overlays: those belong to the interactive bimini.
const strings = toBiminiStringProps(OWNERS_BIMINI_STRINGS);
</script>

<template>
  <g>
    <OwnersBiminiOutline />
    <SolarPanelStringInstance
      v-for="(string, index) in strings"
      :key="index"
      v-bind="string"
    />
  </g>
</template>
