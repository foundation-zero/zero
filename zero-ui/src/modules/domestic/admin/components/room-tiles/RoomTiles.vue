<script setup lang="ts">
import { useRoomStore } from "@/modules/domestic/stores/rooms";
import { provide, toRefs } from "vue";

const { areas, hasPendingRequests } = toRefs(useRoomStore());

provide("disabled", hasPendingRequests);
</script>

<template>
  <section
    v-for="area in areas"
    :key="area.name"
    class="pb-8"
  >
    <header class="flex items-center pb-2 font-bold tracking-wider uppercase md:pb-4 md:text-lg">
      {{ area.name }}

      <span class="grow" />
      <slot
        name="header"
        v-bind="{ area }"
      />
    </header>
    <ul
      class="3xl:grid-cols-6 grid gap-4 transition-all sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-4 2xl:grid-cols-5"
      :class="{
        'opacity-50': hasPendingRequests,
      }"
    >
      <slot
        v-for="room in area.rooms"
        :key="room.id"
        v-bind="{ room, area }"
      />
    </ul>
  </section>
</template>
