<script setup lang="ts">
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/bottom-tabs";
import { useUIStore } from "@/stores/ui";
import { Blinds, LampCeiling, Snowflake } from "lucide-vue-next";
import { toRefs } from "vue";
import { useRoute } from "vue-router";

const { hasScroll, isBottom } = toRefs(useUIStore());
const { path } = toRefs(useRoute());
</script>

<template>
  <Tabs
    as="nav"
    :model-value="path"
    class="fixed bottom-0 w-full"
  >
    <div
      class="absolute bottom-0 left-0 right-0 top-0 bg-background transition-all sm:bg-background"
      :class="{ 'border-t': hasScroll && !isBottom }"
    ></div>

    <TabsList class="relative">
      <RouterLink to="/airco">
        <TabsTrigger value="/airco">
          <Snowflake
            :size="24"
            stroke-width="2"
          />
          A/C
        </TabsTrigger>
      </RouterLink>
      <RouterLink to="/lights">
        <TabsTrigger value="/lights">
          <LampCeiling
            :size="24"
            stroke-width="2"
          />
          Lights
        </TabsTrigger>
      </RouterLink>
      <RouterLink to="/blinds">
        <TabsTrigger value="/blinds">
          <Blinds
            :size="24"
            stroke-width="2"
          />
          Blinds
        </TabsTrigger>
      </RouterLink>
    </TabsList>
  </Tabs>
</template>
