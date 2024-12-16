<script setup lang="ts">
import BarSlider from "@/components/BarSlider.vue";
import RoomTemperature from "@/components/RoomTemperature.vue";
</script>

<template>
  <section class="h-full container flex flex-col justify-evenly">
    <RoomTemperature />
    <div class="flex flex-col items-center">
      <BarSlider />

      <div>
        <div class="inline-flex flex-col items-center justify-center mt-6">
          <span class="text-3xl md:text-5xl font-bold">21</span>
          <span class="text-xs md:text-md font-extralight">Set to</span>
        </div>
        <sup class="text-xl md:text-3xl font-extralight">&deg;</sup>
      </div>
    </div>
  </section>
</template>
