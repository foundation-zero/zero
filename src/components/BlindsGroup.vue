<script setup lang="ts">
import { BlindsControl } from "@/@types";
import { toRefs } from "vue";
import StepSlider from "./ui/step-slider/StepSlider.vue";

const props = defineProps<{ name: string; blinds: BlindsControl[] }>();
const { blinds, name } = toRefs(props);
</script>

<template>
  <article>
    <header class="text-xs uppercase">{{ name }}</header>
    <ul
      class="grid divide-x border"
      :class="{ 'grid-cols-1': blinds.length === 1, 'grid-cols-2': blinds.length === 2 }"
    >
      <li
        v-for="blind in blinds"
        :key="blind.name"
      >
        <span class="text-md"> {{ blind.name }}</span>
        <StepSlider
          :model-value="[blind.position]"
          :max="100"
          :min="0"
          :min-steps-between-thumbs="3"
          :steps="6"
          @update:model-value="(val) => (blind.position = val![0])"
        />
      </li>
    </ul>
  </article>
</template>
