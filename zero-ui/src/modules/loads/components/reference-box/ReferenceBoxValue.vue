<script setup lang="ts">
import { cn } from "@/modules/common/lib/utils";
import { HTMLAttributes } from "vue";
import { formatLoadFn } from "../../lib/utils";
import { Nullable } from "@/modules/common/types";
import { VariableUnit } from "../../types";
import AnimatedNumber from "@/modules/common/components/animated-number/AnimatedNumber.vue";

const props = defineProps<{
  class?: HTMLAttributes["class"];
  type: VariableUnit;
  value: Nullable<number> | undefined;
}>();
</script>

<template>
  <div
    data-slot="target-box-value"
    :class="
      cn(
        'border-attention text-constructive font-headers relative rounded-sm border px-2 text-sm font-semibold',
        props.class,
      )
    "
  >
    <AnimatedNumber
      :to="props.value"
      :format="formatLoadFn(props.type)"
    />
  </div>
</template>
