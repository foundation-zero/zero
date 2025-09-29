<script setup lang="ts">
import type { SelectValueProps } from "reka-ui";
import { SelectValue } from "reka-ui";
import { Badge } from "../badge";

const props = defineProps<SelectValueProps>();
</script>

<template>
  <SelectValue
    data-slot="select-value"
    v-bind="props"
    class="flex grow items-center justify-between gap-2"
  >
    <template #default="{ modelValue }">
      <slot />
      <Badge
        variant="secondary"
        type="number"
      >
        {{ Array.isArray(modelValue) ? modelValue.length : 0 }}
      </Badge>
    </template>
  </SelectValue>
</template>
