<script setup lang="ts">
import { useRoomStore } from "@/stores/rooms";
import { useUIStore } from "@/stores/ui";
import { toRefs } from "vue";

const { areas } = toRefs(useRoomStore());
const { showSideNav } = toRefs(useUIStore());
</script>

<template>
  <section
    v-for="area in areas"
    :key="area.name"
    class="pb-8 text-[0.8rem] md:pb-12 md:text-[0.9rem] lg:text-[0.95rem] xl:text-[1.2rem] portrait:lg:text-[1rem]"
  >
    <header
      class="border-b pb-2 text-rxl font-bold uppercase tracking-tight text-primary/75 dark:text-primary/65 md:pb-4"
    >
      {{ area.name }}
    </header>
    <ul
      class="mt-4 grid grid-cols-2 gap-4 text-rbase transition-all md:mt-6"
      :class="{
        'md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-4': !showSideNav,
        'md:grid-cols-2 lg:grid-cols-3 2xl:grid-cols-4': showSideNav,
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
