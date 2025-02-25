<script setup lang="ts">
import { toRefs } from "vue";
import BottomNavigation from "./components/BottomNavigation.vue";
import RoomSelector from "./components/containers/room-selector/RoomSelector.vue";
import NavPills from "./components/NavPills.vue";
import ToggleAV from "./components/ToggleAV.vue";
import TopNavigation from "./components/TopNavigation.vue";
import { ProgressBar } from "./components/ui/progress-bar";
import { useRoomStore } from "./stores/rooms";
import { useUIStore } from "./stores/ui";

const { breakpoints } = toRefs(useUIStore());
const { hasPendingMutations } = toRefs(useRoomStore());
</script>

<template>
  <main class="flex h-svh flex-col pt-[96px]">
    <RouterView />
  </main>
  <TopNavigation>
    <ProgressBar :pending="hasPendingMutations" />
    <template #left>
      <RoomSelector />
    </template>
    <template #center>
      <NavPills v-if="!breakpoints.phone" />
    </template>
    <template #right>
      <ToggleAV />
    </template>
  </TopNavigation>
  <BottomNavigation v-if="breakpoints.phone" />
</template>

<style scoped></style>
