<script setup lang="ts">
import { cn } from "@common/lib/utils";
</script>

<template>
  <div :class="cn('flex items-center', String($attrs.class))">
    <slot name="left">
      <span class="flex w-1/4 items-center">
        <slot name="left-content" />
      </span>
    </slot>
    <span class="grow" />
    <slot name="center" />
    <span class="grow" />
    <slot name="right">
      <span
        class="flex items-center justify-end"
        :class="{ 'w-1/4': $slots.center }"
      >
        <slot name="right-content" />
      </span>
    </slot>
  </div>
</template>
