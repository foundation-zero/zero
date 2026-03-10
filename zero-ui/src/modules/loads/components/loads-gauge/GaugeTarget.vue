<script setup lang="ts">
import { VariableUnit } from "../../types";
import ReferenceBox from "../reference-box/ReferenceBox.vue";
import ReferenceBoxValue from "../reference-box/ReferenceBoxValue.vue";

import { cn } from "@/modules/common/lib/utils";
import { HTMLAttributes } from "vue";

const props = defineProps<{
  class?: HTMLAttributes["class"];
  target?: number;
}>();
</script>

<template>
  <ReferenceBox :class="cn(props.class)">
    <ReferenceBoxValue
      :value="target"
      :type="VariableUnit.Tonne"
    />
    <slot />
  </ReferenceBox>
</template>
