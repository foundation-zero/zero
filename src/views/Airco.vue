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
  <section class="container flex h-full flex-col justify-evenly">
    <RoomTemperature />
    <div class="flex flex-col items-center rounded-xl border bg-muted/30 py-10 md:mx-8">
      <div class="my-4 h-[300px] w-[150px] overflow-hidden">
        <HeavySlider
          v-model:model-value="value"
          :max="24"
          :min="17.6"
          :min-steps-between-thumbs="3"
          :class="{ 'opacity-70': isOff }"
          :step="0.1"
        />
      </div>

      <div class="mt-6 flex flex-col items-center justify-center">
        <div class="relative inline-flex items-end">
          <span class="text-3xl font-bold uppercase md:text-5xl">
            <span>{{ !isOff ? Math.floor(value[0]) : "Off" }}</span>
          </span>
          <span
            v-if="!isOff"
            class="ml-0.5 text-sm font-light max-md:mb-[2.5px] md:text-2xl"
          >
            {{ Math.round((value[0] % 1) * 10) }}
          </span>
          <sup
            v-show="!isOff"
            class="absolute -top-1 right-0 pt-1 text-2xl font-light max-md:mt-[-2px] md:-top-1.5 md:mr-[1.5px] md:text-3xl"
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
