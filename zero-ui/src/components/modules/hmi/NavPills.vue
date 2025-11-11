<script setup lang="ts">
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/shared/tab-links";
import { THRSModules } from "@/lib/consts.types";

defineProps<{ modules: Array<keyof THRSModules> }>();
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
        v-for="key in modules"
        :key="key"
        :value="key"
        class="font-headers h-16 text-lg font-semibold capitalize md:text-xl lg:text-2xl"
      >
        {{ key }}
      </TabsTrigger>
    </TabsList>
  </Tabs>
</template>
