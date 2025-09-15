<script setup lang="ts">
import { useRoomStore } from "@/stores/rooms";
import { useUIStore } from "@/stores/ui";
import { provide, toRefs } from "vue";

const { areas, hasPendingRequests } = toRefs(useRoomStore());
const { showSideNav } = toRefs(useUIStore());

provide("disabled", hasPendingRequests);
</script>

<template>
  <section
    v-for="area in areas"
    :key="area.name"
    class="pb-8 text-[0.8rem] md:pb-12 md:text-[0.9rem] lg:text-[0.95rem] xl:text-[1.2rem] portrait:lg:text-[1rem]"
  >
    <header
      class="text-rxl text-muted-foreground flex items-center pb-2 font-bold tracking-wider uppercase md:pb-4"
    >
      {{ area.name }}

      <span class="grow" />
      <slot
        name="header"
        v-bind="{ area }"
      />
    </header>
    <ul
      class="text-rbase grid grid-cols-2 gap-4 transition-all"
      :class="{
        'md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-4': !showSideNav,
        'md:grid-cols-2 lg:grid-cols-3 2xl:grid-cols-4': showSideNav,
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
