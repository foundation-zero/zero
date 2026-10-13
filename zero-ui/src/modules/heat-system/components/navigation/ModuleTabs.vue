<script setup lang="ts">
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import RouterLinkWithFallback from "@/modules/common/components/RouterLinkWithFallback.vue";
import { ThrsModules } from "@/modules/heat-system-simulation/lib/consts";
import { Component, computed } from "vue";
import { useRoute } from "vue-router";

defineProps<{ modules: Array<keyof ThrsModules>; activeModule?: keyof ThrsModules }>();

const currentRoute = useRoute();
const supportedViews = computed(
  () => (currentRoute.meta.views as Partial<Record<keyof ThrsModules, Component>>) ?? {},
);
</script>

<template>
  <Tabs :model-value="activeModule">
    <TabsList
      class="backdrop-blur-md"
      as="nav"
    >
      <RouterLinkWithFallback
        v-for="key in modules"
        :key="key"
        :to="{
          name: currentRoute.name as string,
          params: { module: key },
        }"
        :disabled="!supportedViews[key]"
      >
        <TabsTrigger
          :value="key"
          class="uppercase"
          :disabled="!supportedViews[key]"
        >
          {{ key }}
        </TabsTrigger>
      </RouterLinkWithFallback>
    </TabsList>
  </Tabs>
</template>
