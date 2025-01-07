<script setup lang="ts">
import RoomTemperature from "@/components/RoomTemperature.vue";
import { HeavySlider } from "@/components/ui/heavy-slider";
import { computed, ref } from "vue";

let _value = ref(21);
const MIN_VALUE = 17.9;

const value = computed<number[]>({
  get() {
    return [_value.value];
  },
  set([val]: number[]) {
    if (val < MIN_VALUE) return;

    _value.value = val;
  },
});
const isOff = computed(() => value.value[0] == MIN_VALUE);
</script>

<template>
  <section class="h-full container flex flex-col justify-evenly">
    <RoomTemperature />
    <div class="flex flex-col items-center md:mx-8 bg-muted/30 rounded-xl py-10 border">
      <div class="h-[300px] w-[150px] my-4 overflow-hidden">
        <HeavySlider
          v-model:model-value="value"
          :max="24"
          :min="17.6"
          :min-steps-between-thumbs="3"
          :class="{ 'opacity-70': isOff }"
          :step="0.1"
        />
      </div>

      <div class="flex flex-col items-center justify-center mt-6">
        <div class="inline-flex items-end relative">
          <span class="text-3xl md:text-5xl font-bold uppercase">
            <span>{{ !isOff ? Math.floor(value[0]) : "Off" }}</span>
          </span>
          <span
            v-if="!isOff"
            class="font-light text-sm md:text-2xl ml-0.5 max-md:mb-[2.5px]"
          >
            {{ Math.round((value[0] % 1) * 10) }}
          </span>
          <sup
            v-show="!isOff"
            class="text-2xl md:text-3xl font-light pt-1 absolute max-md:mt-[-2px] -top-1 md:-top-1.5 md:mr-[1.5px] right-0"
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
