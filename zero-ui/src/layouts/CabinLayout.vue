<script setup lang="ts">
import TopNavigation from "@components/shared/TopNavigation.vue";
import { ProgressBar } from "@components/shared/progress-bar";
import AsAdmin from "@components/shared/with-role/AsAdmin.vue";
import SideNav from "@modules/admin/side-nav/SideNav.vue";
import BottomNavigation from "@modules/cabin/BottomNavigation.vue";
import NavPills from "@modules/cabin/NavPills.vue";
import ToggleAV from "@modules/cabin/ToggleAV.vue";
import { Sidebar } from "lucide-vue-next";
import { provide, toRefs } from "vue";
import { useRoomStore } from "../stores/rooms";
import { useUIStore } from "../stores/ui";

const { showSideNav, breakpoints, toggleNav } = toRefs(useUIStore());
const { hasPendingRequests, currentRoom } = toRefs(useRoomStore());

provide("disabled", hasPendingRequests);
</script>

<template>
  <main class="flex h-[100svh] flex-row md:flex-nowrap">
    <AsAdmin>
      <SideNav :show="showSideNav" />
    </AsAdmin>
    <article
      class="flex w-full flex-col items-center pt-[64px] sm:pt-[96px]"
      :class="{
        'border-l border-r bg-[hsl(var(--primary)/0.025)] px-0 2xl:container xl:px-6':
          !breakpoints.touch,
        'pending opacity-50': hasPendingRequests,
      }"
    >
      <slot />
    </article>
  </main>
  <TopNavigation :class="{ 'md:!left-[250px] lg:!left-[300px]': showSideNav }">
    <ProgressBar
      :pending="hasPendingRequests"
      class="absolute left-0 right-0"
    />
    <template #left>
      <div
        class="flex items-center text-base font-bold xl:text-lg"
        data-testid="room-name"
      >
        <AsAdmin>
          <button
            class="flex cursor-pointer items-center gap-2"
            @click="toggleNav()"
          >
            <Sidebar
              v-if="breakpoints.touch"
              stroke-width="1.5"
            />
            <span>{{ currentRoom.name }}</span>
          </button>
          <template #fallback>
            <span>{{ currentRoom.name }}</span>
          </template>
        </AsAdmin>
      </div>
    </template>
    <template #center>
      <NavPills class="absolute left-[50%] translate-x-[-50%] transition-all max-md:hidden" />
    </template>
    <template #right>
      <ToggleAV />
    </template>
  </TopNavigation>
  <BottomNavigation class="md:hidden" />
</template>
