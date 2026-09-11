<script setup lang="ts">
import { ZiHeatBatteryEmpty } from "@/modules/common/components/icons";
</script>

<template>
  <header
    class="text-foreground font-heading flex items-center gap-2 text-base font-bold tracking-widest uppercase"
  >
    <ZiHeatBatteryEmpty
      class="h-5 w-5"
      icon-class="fill-brand"
    />
    <slot />
  </header>
</template>
