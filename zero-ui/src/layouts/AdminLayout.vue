<script setup lang="ts">
import { useRoomStore } from "@/stores/rooms";
import { useUIStore } from "@/stores/ui";
import TopNavigation from "@components/shared/TopNavigation.vue";
import { ProgressBar } from "@components/shared/progress-bar";
import SideNav from "@modules/admin/side-nav/SideNav.vue";
import { Sidebar } from "lucide-vue-next";
import { provide, toRefs } from "vue";

const { hasPendingRequests } = toRefs(useRoomStore());
const { showSideNav, breakpoints, toggleNav } = toRefs(useUIStore());

provide("showSideNav", showSideNav);
</script>

<template>
  <main class="flex h-svh flex-row md:flex-nowrap">
    <SideNav :show="showSideNav" />
    <article
      class="flex w-full flex-col px-4 md:px-6"
      :class="{
        '2xl:container': !breakpoints.touch,
        'pt-[56px] md:pt-[64px]': breakpoints.touch,
        'pt-3 md:pt-4': !breakpoints.touch,
      }"
    >
      <slot />
    </article>
    <TopNavigation :class="{ 'md:left-[250px]! lg:left-[300px]!': showSideNav }">
      <ProgressBar
        :pending="hasPendingRequests"
        class="absolute right-0 left-0"
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
