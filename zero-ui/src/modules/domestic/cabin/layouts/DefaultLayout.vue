<script setup lang="ts">
import { provide, toRefs } from "vue";
import { useRoomStore } from "../../stores/rooms";

const { hasPendingRequests } = toRefs(useRoomStore());

provide("disabled", hasPendingRequests);
</script>

<template>
  <article class="flex flex-col items-center">
    <RouterView />
  </article>
</template>
