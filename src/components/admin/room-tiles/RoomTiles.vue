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
    class="landscape:lg:[1rem] pb-12 text-[1rem] sm:text-[0.8rem] xl:text-[1rem]"
  >
    <header
      class="border-b pb-2 text-rbase font-bold uppercase tracking-tight text-primary/75 dark:text-primary/65 md:text-rxl"
    >
      {{ area.name }}
    </header>
    <ul
      class="grid grid-cols-1 gap-4 text-rbase transition-all md:mt-4"
      :class="{
        'md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-4': !showSideNav,
        'md:grid-cols-2 lg:grid-cols-3 2xl:grid-cols-4': showSideNav,
      }"
    >
      <li
        v-for="room in area.rooms"
        :key="room.id"
        class="relative flex aspect-video flex-col justify-between rounded-lg bg-primary/5 px-2.5 py-1 text-primary/80 dark:bg-primary/10 lg:px-3 lg:py-2"
      >
        <slot
          name="top-left"
          v-bind="{ room }"
        >
          <span class="md:text-rlg">{{ room.name }}</span>
        </slot>

        <span
          class="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 text-r6xl font-bold"
        >
          <slot
            name="center"
            v-bind="{ room }"
          />
        </span>

        <span class="flex w-full items-center">
          <slot
            name="bottom-left"
            v-bind="{ room }"
          />
          <span class="grow" />
          <slot
            name="bottom-right"
            v-bind="{ room }"
          />
        </span>
      </li>
    </ul>
  </section>
</template>
