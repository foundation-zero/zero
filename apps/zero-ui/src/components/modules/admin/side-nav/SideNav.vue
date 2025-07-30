<script setup lang="ts">
import { useRoomStore } from "@/stores/rooms";
import { useUIStore } from "@/stores/ui";

import { Cross2Icon } from "@radix-icons/vue";
import { toRefs, watch } from "vue";
import { useRoute } from "vue-router";
import AreasWithRooms from "./AreasWithRooms.vue";
import Outside from "./Outside.vue";
import SystemControlsList from "./SystemControlsList.vue";

const show = defineModel<boolean>("show", { required: true });

const { areas, currentRoomId } = toRefs(useRoomStore());
const { breakpoints, showSideNav } = toRefs(useUIStore());
const { toggleNav } = useUIStore();
const route = useRoute();

const toggle = () => {
  // Hide the side nav on mobile phones if route has changed
  if (showSideNav.value) {
    toggleNav(!breakpoints.value.phone);
  }
};

watch([currentRoomId, route], toggle);
</script>

<template>
  <aside :class="{ show }">
    <nav role="navigation">
      <div class="pl-3 pr-6">
        <h2
          class="flex items-center justify-between pl-3 text-2xl font-bold text-primary lg:text-3xl"
        >
          {{ $t("labels.zero") }}
          <Outside />
          <button
            class="text-xl font-normal md:hidden"
            @click="() => toggleNav(false)"
          >
            <Cross2Icon class="h-5 w-5" />
          </button>
        </h2>
      </div>
      <div class="mb-12 mt-6 grid gap-3 px-3">
        <SystemControlsList />
      </div>

      <div class="grid gap-5 px-3">
        <AreasWithRooms
          :areas="areas"
          :current-room-id="currentRoomId"
        />
      </div>
    </nav>
  </aside>
</template>

<style lang="scss" scoped>
aside {
  @apply z-10 h-full w-0 flex-shrink-0 overflow-visible transition-all;
}

aside.show {
  @apply md:min-w-[250px] lg:min-w-[300px];
}

aside:not(.show) {
  nav {
    @apply -translate-x-full;
  }
}

nav {
  @apply fixed left-0 top-0 h-[100svh] overflow-y-auto border-r border-border-light bg-background-light py-3 transition-transform dark:border-border-dark dark:bg-background-dark max-md:w-full md:min-w-[250px] lg:min-w-[300px];
}
</style>
