<script setup lang="ts">
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Blinds, LampCeiling, Snowflake } from "lucide-vue-next";
import { toRefs } from "vue";
import { useRoute } from "vue-router";
const { path } = toRefs(useRoute());
</script>

<template>
  <Tabs
    :model-value="path"
    class="absolute left-[50%] translate-x-[-50%] max-md:hidden"
  >
    <TabsList
      class="bg-black dark:bg-white !bg-opacity-5 backdrop-blur-md"
      as="nav"
    >
      <RouterLink to="/airco">
        <TabsTrigger value="/airco">
          <Snowflake
            :size="16"
            stroke-width="2"
            class="inline mr-2"
          />
          Airco
        </TabsTrigger>
      </RouterLink>
      <RouterLink to="/lights">
        <TabsTrigger value="/lights">
          <LampCeiling
            :size="16"
            stroke-width="2"
            class="inline mr-2"
          />
          Lights
        </TabsTrigger>
      </RouterLink>
      <RouterLink to="/blinds">
        <TabsTrigger value="/blinds">
          <Blinds
            :size="16"
            stroke-width="2"
            class="inline mr-2"
          />
          Blinds
        </TabsTrigger>
      </RouterLink>
    </TabsList>
  </Tabs>
</template>
