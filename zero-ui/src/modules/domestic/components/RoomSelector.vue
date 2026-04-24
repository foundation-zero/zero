<script setup lang="ts">
import { RiHotelBedLine } from "@remixicon/vue";
import { toRefs } from "vue";
import { useRoomStore } from "../stores/rooms";

const { currentRoom } = toRefs(useRoomStore());
</script>

<template>
  <h3
    class="border-attention ml-2 flex items-center gap-1.5 py-2.5 text-sm font-medium uppercase md:text-base!"
    data-testid="room-name"
  >
    <RiHotelBedLine class="inline size-3.5 md:size-4" />
    {{ currentRoom.name }}
  </h3>
</template>
