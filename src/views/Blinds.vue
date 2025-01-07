<script setup lang="ts">
import { StepSlider } from "@/components/ui/step-slider";
import { ref } from "vue";

const value = ref([100 / 6]);
</script>

<template>
  <section class="container flex h-full flex-col justify-evenly">
    <div class="flex flex-col items-center rounded-xl border bg-muted/30 py-10">
      <div class="h-[300px] w-[150px]">
        <StepSlider
          v-model:model-value="value"
          :max="100"
          :min="0"
          :min-steps-between-thumbs="3"
          :steps="6"
        />
      </div>

      <div class="mt-6 flex flex-col items-center justify-center">
        <div class="inline-flex items-end">
          <span class="text-3xl font-bold uppercase md:text-5xl">
            <span>{{ Math.round(100 - value[0]) }}</span>
          </span>
          <span class="ml-0.5">&percnt;</span>
        </div>
      </div>
    </div>
  </section>
</template>
