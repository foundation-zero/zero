<script setup lang="ts">
import BarSlider from "@/components/BarSlider.vue";
import RoomTemperature from "@/components/RoomTemperature.vue";
</script>

<template>
  <RoomTemperature class="mt-16" />
  <div class="flex flex-col items-center mt-[68px] md:mt-[96px]">
    <BarSlider />

    <div class="flex flex-col items-center justify-center mt-6">
      <div>
        <span class="text-3xl font-bold">21</span>
        <sup class="text-xl -ml-0 font-extralight">&deg;</sup>
      </div>
      <span class="text-xs font-extralight -ml-2.5">Set to</span>
    </div>
  </div>
</template>
