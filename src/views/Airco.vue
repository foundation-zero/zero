<script setup lang="ts">
import RoomTemperature from "@/components/RoomTemperature.vue";
import { HeavySlider } from "@/components/ui/heavy-slider";
import { List, ListItem, ListRoot } from "@/components/ui/list";
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
  <section
    class="container flex grow flex-col items-center justify-center max-md:pb-[64px] md:pb-[32px]"
  >
    <RoomTemperature class="mb-8 w-full" />

    <div class="flex w-full flex-wrap justify-center">
      <ListRoot class="w-full pb-6 md:w-1/2 md:px-3 xl:w-1/3 landscape:lg:w-1/3">
        <List
          orientation="horizontal"
          :size="1"
        >
          <ListItem class="flex-col pb-6">
            <span class="text-lg font-medium">A/C</span>
            <HeavySlider
              v-model:model-value="value"
              class="aspect-[1/2] !h-[40svh] !w-auto"
              :max="24"
              :min="17.6"
              :min-steps-between-thumbs="3"
              :class="{ 'opacity-70': isOff }"
              :step="0.1"
            />

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
          </ListItem>
        </List>
      </ListRoot>
    </div>
  </section>
</template>
