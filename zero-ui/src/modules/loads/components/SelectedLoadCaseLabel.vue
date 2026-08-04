<script setup lang="ts">
import { QueryLoadCase } from "../types/queries";

defineProps<{ loadCase?: QueryLoadCase | null }>();
</script>

<template>
  <p
    v-if="loadCase"
    class="text-muted-foreground text-xs leading-none font-medium whitespace-nowrap"
  >
    Sailpack model: {{ loadCase.name }} AWA: {{ loadCase.awa.toFixed(1) }}° AWS:
    {{ loadCase.aws.toFixed(1) }} kts Heel: {{ loadCase.heel.toFixed(1) }}° TWA:
    {{ loadCase.twa.toFixed(1) }}° TWS: {{ loadCase.tws.toFixed(1) }} kts
  </p>
</template>
