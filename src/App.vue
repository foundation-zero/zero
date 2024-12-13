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
  <main class="container px-0 pt-[70px] h-full max-sm:pb-[60px] flex flex-col justify-evenly">
    <RouterView />
  </main>
  <BottomNavigation class="md:hidden" />
</template>

<style scoped></style>
