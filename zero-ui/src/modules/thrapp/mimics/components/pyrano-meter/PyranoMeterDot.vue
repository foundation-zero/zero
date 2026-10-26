<script setup lang="ts">
defineProps<{ x?: number | string; y?: number | string }>();
</script>

<template>
  <!-- Top-down pyranometer marker, as used on the bimini layouts. -->
  <svg
    :x="x"
    :y="y"
    width="10"
    height="10"
    viewBox="0 0 10 10"
    opacity="0.5"
    data-slot="pyranometer-dot"
  >
    <circle
      cx="5"
      cy="5"
      r="4.5"
      class="fill-muted stroke-attention"
    />
    <circle
      cx="5"
      cy="5"
      r="3"
      class="fill-attention-muted"
    />
  </svg>
</template>
