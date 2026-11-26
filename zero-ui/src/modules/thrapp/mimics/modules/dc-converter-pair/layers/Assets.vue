<script setup lang="ts">
import { computed } from "vue";
import { BranchFields } from "../dc-converter-pair.types";
import { MimicComponentType } from "@/modules/thrapp/types";
import { getTooltipContext } from "../../../data";
import { PowerConverterInstance } from "../../../instances";

const props = defineProps<{ fields: BranchFields<MimicComponentType.PowerConverter> }>();

const getContext = getTooltipContext(MimicComponentType.PowerConverter);
// Not `map(getContext)`: map passes the index, which getContext takes as `arrayIndexIfMultiple`.
const converters = computed(() => props.fields.map((field) => getContext(field)));
</script>

<template>
  <g>
    <PowerConverterInstance
      x="0"
      y="0"
      v-bind="converters[0]"
    />
    <PowerConverterInstance
      x="0"
      y="205"
      v-bind="converters[1]"
    />
  </g>
</template>
