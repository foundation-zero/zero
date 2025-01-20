<script setup lang="ts">
import { toRefs } from "vue";
import BottomNavigation from "./components/BottomNavigation.vue";
import RoomSelectorDialog from "./components/containers/room-selector/RoomSelectorDialog.vue";
import RoomSelectorDrawer from "./components/containers/room-selector/RoomSelectorDrawer.vue";
import NavPills from "./components/NavPills.vue";
import ToggleAV from "./components/ToggleAV.vue";
import TopNavigation from "./components/TopNavigation.vue";
import { useUIStore } from "./stores/ui";

const { breakpoints } = toRefs(useUIStore());
</script>

<template>
  <main class="flex h-svh flex-col pt-[96px]">
    <RouterView />
  </main>
  <TopNavigation>
    <template #left>
      <RoomSelectorDrawer v-if="breakpoints.phone" />
      <RoomSelectorDialog v-if="!breakpoints.phone" />
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
