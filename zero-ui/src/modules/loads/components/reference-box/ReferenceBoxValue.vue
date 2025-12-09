<script setup lang="ts">
import { cn } from "@/modules/common/lib/utils";
import { computed, HTMLAttributes } from "vue";
import { formatLoad } from "../../lib/utils";
import { VariableType } from "../../types";

const props = defineProps<{
  class?: HTMLAttributes["class"];
  type: VariableType;
  value: number | undefined;
}>();

const formattedTarget = computed(() => formatLoad(props.value, props.type));
</script>

<template>
  <div
    data-slot="target-box-value"
    :class="
      cn(
        'border-attention text-constructive font-headers relative rounded-sm border px-2 text-xl font-semibold',
        props.class,
      )
    "
  >
    {{ formattedTarget }}
  </div>
</template>
