<script setup lang="ts">
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import RouterLinkWithFallback from "@/modules/common/components/RouterLinkWithFallback.vue";
import { ThrsModules } from "@/modules/thrs/lib/consts";

defineProps<{ modules: Array<keyof ThrsModules>; activeModule?: keyof ThrsModules }>();

const SUPPORTED_MIMICS: Array<keyof ThrsModules> = ["dhw"];
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
          name: 'thrapp/mimics',
          params: { module: key },
        }"
        :disabled="!SUPPORTED_MIMICS.includes(key)"
      >
        <TabsTrigger
          :value="key"
          class="uppercase"
          :disabled="!SUPPORTED_MIMICS.includes(key)"
        >
          {{ key }}
        </TabsTrigger>
      </RouterLinkWithFallback>
    </TabsList>
  </Tabs>
</template>
