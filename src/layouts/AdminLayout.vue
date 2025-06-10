<script setup lang="ts">
import SideNav from "@/components/admin/side-nav/SideNav.vue";
import TopNavigation from "@/components/TopNavigation.vue";
import { ProgressBar } from "@/components/ui/progress-bar";
import { useRoomStore } from "@/stores/rooms";
import { useUIStore } from "@/stores/ui";
import { Sidebar } from "lucide-vue-next";
import { provide, toRefs } from "vue";

const { hasPendingRequests } = toRefs(useRoomStore());
const { showSideNav, breakpoints, toggleNav } = toRefs(useUIStore());

provide("showSideNav", showSideNav);
</script>

<template>
  <main class="flex h-[100svh] flex-row md:flex-nowrap">
    <SideNav :show="showSideNav" />
    <article
      class="flex w-full flex-col px-4 pt-[56px] md:px-6 md:pt-[64px]"
      :class="{
        '2xl:container': !breakpoints.touch,
      }"
    >
      <slot />
    </article>
    <TopNavigation :class="{ 'md:!left-[250px] lg:!left-[300px]': showSideNav }">
      <ProgressBar
        :pending="hasPendingRequests"
        class="absolute left-0 right-0"
      />
      <template #left>
        <button
          v-if="breakpoints.touch"
          @click="toggleNav()"
        >
          <Sidebar stroke-width="1.5" />
        </button>
      </template>

      <template
        v-if="$route.meta.settings"
        #right
      >
        <component :is="$route.meta.settings" />
      </template>
    </TopNavigation>
  </main>
</template>
