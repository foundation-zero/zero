<template>
  <div>
    <slot />
  </div>
</template>

<script setup lang="ts">
import { useRoomStore } from "@/stores/rooms";

const store = useRoomStore();

defineExpose({ store });
</script>
