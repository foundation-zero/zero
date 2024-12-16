<script setup lang="ts">
import TopNavigation from "./components/TopNavigation.vue";
import BottomNavigation from "./components/BottomNavigation.vue";
import RoomSelector from "./components/RoomSelector.vue";
import ToggleAV from "./components/ToggleAV.vue";
</script>

<template>
  <main class="pt-[96px] flex flex-col h-svh pb-[96px]">
    <RouterView />
  </main>
  <TopNavigation>
    <template #left>
      <RoomSelector />
    </template>
    <template #right>
      <ToggleAV />
    </template>
  </TopNavigation>
  <BottomNavigation class="md:hidden" />
</template>

<style scoped></style>
