<script setup lang="ts">
import { useDebounceFn, useTimeoutFn, useWindowSize } from "@vueuse/core";
import { ref, watch } from "vue";

const { width } = useWindowSize();

const show = ref(true);
const onResize = useDebounceFn(() => {
  show.value = false;
  useTimeoutFn(() => (show.value = true), 0);
}, 100);

watch(width, onResize);
</script>

<template>
  <slot v-if="show" />
</template>
