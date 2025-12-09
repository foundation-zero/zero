<script setup lang="ts">
import { THRSModules } from "@/modules/thrs/lib/consts.types";
import { Tabs, TabsList, TabsTrigger } from "@common/components/tab-links";
import { RouterLink, useRoute } from "vue-router";

defineProps<{ modules: Array<keyof THRSModules> }>();
const activeModule = defineModel<string>("activeModule", { required: true });
const currentRoute = useRoute();
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
      <RouterLink
        v-for="key in modules"
        :key="key"
        :to="{ name: currentRoute.name, params: { module: key } }"
      >
        <TabsTrigger
          :value="key"
          class="font-headers h-16 text-base font-semibold capitalize md:text-xl lg:text-2xl"
        >
          {{ key }}
        </TabsTrigger>
      </RouterLink>
    </TabsList>
  </Tabs>
</template>
