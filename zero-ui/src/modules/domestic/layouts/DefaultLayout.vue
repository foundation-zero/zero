<script setup lang="ts">
import { TopNav } from "@/modules/common/components/navigation";
import { useRouter } from "vue-router";

const { currentRoute } = useRouter();
</script>

<template>
  <main class="h-svh pt-[10em] pb-8 md:pt-[12em]">
    <slot />
  </main>
  <TopNav>
    <component
      :is="currentRoute.meta.mainNav"
      v-if="currentRoute.meta.mainNav"
    />
    <component
      :is="currentRoute.meta.subNav"
      v-if="currentRoute.meta.subNav"
    />
    <component
      :is="currentRoute.meta.infoNav"
      v-if="currentRoute.meta.infoNav"
    />
  </TopNav>
  <component
    :is="currentRoute.meta.bottomNav"
    v-if="currentRoute.meta.bottomNav"
  />
</template>
