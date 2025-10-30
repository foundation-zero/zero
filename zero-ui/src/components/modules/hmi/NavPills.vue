<script setup lang="ts">
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/shared/tab-links";

defineProps<{ modules: Record<string, unknown> }>();
const activeModule = defineModel<string>("activeModule", { required: true });
</script>

<template>
  <Tabs
    v-model="activeModule"
    data-testid="hmi-nav"
  >
    <TabsList
      as="nav"
      class="py-0"
    >
      <TabsTrigger
        v-for="(_, key) in modules"
        :key="key"
        :value="key"
        class="font-headers h-16 text-lg font-semibold capitalize md:text-xl lg:text-2xl"
      >
        {{ key }}
      </TabsTrigger>
    </TabsList>
  </Tabs>
</template>
