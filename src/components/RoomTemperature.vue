<script setup lang="ts">
import { Room } from "@/@types";

defineProps<{ room: Room }>();
</script>

<template>
  <article class="w-100 flex items-center justify-around">
    <div>
      <span class="inline-flex flex-col items-center justify-center">
        <span class="text-5xl font-bold lg:text-7xl md:portrait:text-7xl">{{
          room.actualTemperature
        }}</span>
        <span class="text-md font-extralight">Inside</span>
      </span>
      <sup class="text-3xl font-extralight lg:text-5xl md:portrait:text-5xl">&deg;</sup>
    </div>

    <div>
      <span class="inline-flex flex-col items-center justify-center">
        <span class="text-5xl font-bold lg:text-7xl md:portrait:text-7xl">33</span>
        <span class="text-md font-extralight">Outside</span>
      </span>
      <sup class="text-3xl font-extralight lg:text-5xl md:portrait:text-5xl">&deg;</sup>
    </div>
  </article>
</template>
