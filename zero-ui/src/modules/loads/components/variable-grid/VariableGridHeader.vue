<script setup lang="ts">
import { cn } from "@/modules/common/lib/utils";
</script>

<template>
  <div :class="cn('col-span-full flex items-center gap-2')">
    <slot />
    <hr class="border-border-subtle flex-grow border-t" />
  </div>
</template>
