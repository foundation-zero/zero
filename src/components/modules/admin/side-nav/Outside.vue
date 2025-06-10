<script setup lang="ts">
import { Droplets, ThermometerSun } from "lucide-vue-next";
</script>

<template>
  <div class="flex items-center justify-between gap-4 text-base font-normal">
    <span class="flex items-center">
      <Droplets
        :size="16"
        stroke-width="1"
      />
      <span class="ml-1">65<span class="ml-0.5 text-rxs font-light">&percnt;</span> </span>
    </span>

    <span class="flex items-center">
      <ThermometerSun
        :size="16"
        stroke-width="1"
      />
      <span class="ml-1">33&deg;</span>
    </span>
  </div>
</template>
