<script setup lang="ts">
import { StepSlider } from "@/components/ui/step-slider";
import { ref } from "vue";

const value = ref([100 / 6]);
</script>

<template>
  <section class="h-full container flex flex-col justify-evenly">
    <div class="flex flex-col items-center">
      <div class="h-[300px] w-[150px] my-4">
        <StepSlider
          :max="100"
          :min="0"
          :min-steps-between-thumbs="3"
          :steps="6"
          v-model:model-value="value"
        />
      </div>

      <div class="flex flex-col items-center justify-center mt-6">
        <div class="inline-flex items-end">
          <span class="text-3xl md:text-5xl font-bold uppercase">
            <span>{{ Math.round(100 - value[0]) }}</span>
          </span>
          <span class="ml-0.5">&percnt;</span>
        </div>
      </div>
    </div>
  </section>
</template>
