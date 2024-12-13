<script setup lang="ts">
import TopNavigation from "./components/TopNavigation.vue";
import BottomNavigation from "./components/BottomNavigation.vue";
import RoomSelector from "./components/RoomSelector.vue";
import ToggleAV from "./components/ToggleAV.vue";
</script>

<template>
  <TopNavigation>
    <template #left>
      <RoomSelector />
    </template>
    <template #right>
      <ToggleAV />
    </template>
  </TopNavigation>
  <main class="container px-6 pt-[96px]">
    <RouterView />
  </main>
  <BottomNavigation class="md:hidden" />
</template>

<style scoped></style>
