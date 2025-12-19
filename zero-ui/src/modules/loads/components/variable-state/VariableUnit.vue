<script setup lang="ts">
import { cn } from "@/modules/common/lib/utils";
import { HTMLAttributes, inject } from "vue";
import { LOAD_UNIT } from "../../lib/consts";
import { VariableUnit } from "../../types";

const props = defineProps<{ class?: HTMLAttributes["class"] }>();
const type = inject<VariableUnit>("load-type", VariableUnit.Percentage);
</script>

<template>
  <span
    data-slot="load-unit"
    class="text-disabled-foreground"
    :class="
      cn(
        'absolute top-[0.50em] translate-x-full text-[0.357em] leading-[1] font-normal text-shadow-2xs',
        props.class,
        {
          '-right-[0.25em]': type === VariableUnit.Tonne,
          '-right-[0.10em]': type === VariableUnit.Percentage,
        },
      )
    "
  >
    {{ LOAD_UNIT[type] }}
  </span>
</template>
