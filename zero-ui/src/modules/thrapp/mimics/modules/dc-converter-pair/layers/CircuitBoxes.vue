<script setup lang="ts">
import { computed } from "vue";
import { MimicComponentType } from "@/modules/thrapp/types";
import { getTooltipContext, RegisterField } from "../../../data";
import { ConnectingCircuitInstance } from "../../../instances";

const props = defineProps<{ field: RegisterField<MimicComponentType.ConnectingCircuit> }>();

const circuit = computed(() =>
  getTooltipContext(MimicComponentType.ConnectingCircuit)(props.field),
);
</script>

<template>
  <g>
    <ConnectingCircuitInstance
      x="910"
      y="211"
      width="196"
      height="212"
      inverted
      v-bind="circuit"
    />
  </g>
</template>
