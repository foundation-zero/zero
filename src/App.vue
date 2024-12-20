<script setup lang="ts">
import TopNavigation from "./components/TopNavigation.vue";
import BottomNavigation from "./components/BottomNavigation.vue";
import RoomSelectorDrawer from "./components/containers/room-selector/RoomSelectorDrawer.vue";
import ToggleAV from "./components/ToggleAV.vue";
import { toRefs } from "vue";
import { useUIStore } from "./stores/ui";
import NavPills from "./components/NavPills.vue";
import RoomSelectorDialog from "./components/containers/room-selector/RoomSelectorDialog.vue";

const { breakpoints } = toRefs(useUIStore());
</script>

<template>
  <main class="pt-[96px] flex flex-col h-svh pb-[96px]">
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
