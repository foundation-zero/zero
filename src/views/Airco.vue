<script setup lang="ts">
import RoomTemperature from "@/components/RoomTemperature.vue";
import { HeavySlider } from "@/components/ui/heavy-slider";
import { computed, ref } from "vue";

const value = ref([17.9, 21]);
const isOff = computed(() => value.value[1] == 18.2);
</script>

<template>
  <section class="h-full container flex flex-col justify-evenly">
    <RoomTemperature />
    <div class="flex flex-col items-center">
      <div class="h-[300px] w-[150px] my-4 overflow-hidden">
        <HeavySlider
          :max="24"
          :min="18"
          :min-steps-between-thumbs="3"
          :class="{ 'opacity-70': isOff }"
          :step="0.1"
          v-model:model-value="value"
        />
      </div>

      <div class="flex flex-col items-center justify-center mt-6">
        <div class="inline-flex items-end relative">
          <span class="text-3xl md:text-5xl font-bold uppercase">
            <span>{{ !isOff ? Math.floor(value[1]) : "Off" }}</span>
          </span>
          <span
            class="font-extralight text-xs md:text-lg ml-1 max-sm:mb-1"
            v-if="!isOff"
          >
            {{ Math.round((value[1] % 1) * 10) }}
          </span>
          <sup
            class="text-xl md:text-3xl font-light pt-1 absolute -top-1 right-0"
            v-show="!isOff"
            >&deg;</sup
          >
        </div>
        <span
          class="text-xs font-extralight md:text-base"
          :class="{ invisible: isOff }"
          >Set to</span
        >
      </div>
    </div>
  </section>
</template>
