<script setup lang="ts">
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/bottom-tabs";
import { Blinds, LampCeiling, Snowflake } from "lucide-vue-next";
</script>

<template>
  <Tabs
    default-value="airco"
    class="fixed bottom-0 w-full"
  >
    <TabsList class="">
      <RouterLink to="/airco">
        <TabsTrigger value="airco">
          <Snowflake
            :size="24"
            stroke-width="2"
            class="mb-1"
          />
          Airco
        </TabsTrigger>
      </RouterLink>
      <RouterLink to="/lights">
        <TabsTrigger value="lights">
          <LampCeiling
            :size="24"
            stroke-width="2"
            class="mb-1"
          />
          Lights
        </TabsTrigger>
      </RouterLink>
      <RouterLink to="/blinds">
        <TabsTrigger value="blinds">
          <Blinds
            :size="24"
            stroke-width="2"
            class="mb-1"
          />
          Blinds
        </TabsTrigger>
      </RouterLink>
    </TabsList>
  </Tabs>
</template>
