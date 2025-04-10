<script setup lang="ts">
import { toRefs } from "vue";
import BottomNavigation from "./components/BottomNavigation.vue";
import RoomSelector from "./components/containers/room-selector/RoomSelector.vue";
import RoomSelectorButton from "./components/containers/room-selector/RoomSelectorButton.vue";
import NavPills from "./components/NavPills.vue";
import ToggleAV from "./components/ToggleAV.vue";
import TopNavigation from "./components/TopNavigation.vue";
import { ProgressBar } from "./components/ui/progress-bar";
import { useAuthStore } from "./stores/auth";
import { useRoomStore } from "./stores/rooms";
import { useUIStore } from "./stores/ui";

const { breakpoints } = toRefs(useUIStore());
const { hasPendingMutations } = toRefs(useRoomStore());
const { isAdmin } = toRefs(useAuthStore());
</script>

<template>
  <main class="flex h-svh flex-col pt-[96px]">
    <RouterView />
  </main>
  <TopNavigation>
    <ProgressBar :pending="hasPendingMutations" />
    <template #left>
      <RoomSelector v-if="isAdmin" />
      <RoomSelectorButton v-else />
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
