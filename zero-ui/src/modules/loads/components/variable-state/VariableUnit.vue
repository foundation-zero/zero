<script setup lang="ts">
import { cn } from "@/modules/common/lib/utils";
import { HTMLAttributes, inject } from "vue";
import { LOAD_UNIT } from "../../lib/consts";
import { VariableType } from "../../types";

const props = defineProps<{ class?: HTMLAttributes["class"] }>();
const type = inject<VariableType>("load-type", VariableType.Percentage);
</script>

<template>
  <span
    data-slot="load-unit"
    class="text-disabled-foreground"
    :class="
      cn(
        'text-r4xs absolute top-[0.50em] translate-x-full font-normal text-shadow-2xs',
        props.class,
        {
          '-right-[0.25em]': type === VariableType.Tonnes,
          'right-0': type === VariableType.Percentage,
        },
      )
    "
  >
    {{ LOAD_UNIT[type] }}
  </span>
</template>
