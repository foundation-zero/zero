<script setup lang="ts">
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Blinds, LampCeiling, Snowflake } from "lucide-vue-next";
</script>

<template>
  <Tabs
    default-value="airco"
    class="absolute top-0 w-full mt-5"
  >
    <div class="flex justify-between items-center px-6">
      <slot name="left">
        <div></div>
      </slot>

      <TabsList class="absolute left-[50%] translate-x-[-50%] max-sm:hidden">
        <RouterLink to="/airco">
          <TabsTrigger value="airco">
            <Snowflake
              :size="16"
              stroke-width="2"
              class="inline mr-2"
            />
            Airco
          </TabsTrigger>
        </RouterLink>
        <RouterLink to="/lights">
          <TabsTrigger value="lighting">
            <LampCeiling
              :size="16"
              stroke-width="2"
              class="inline mr-2"
            />
            Lights
          </TabsTrigger>
        </RouterLink>
        <RouterLink to="/blinds">
          <TabsTrigger value="blinds">
            <Blinds
              :size="16"
              stroke-width="2"
              class="inline mr-2"
            />
            Blinds
          </TabsTrigger>
        </RouterLink>
      </TabsList>

      <slot name="right">
        <div></div>
      </slot>
    </div>
  </Tabs>
</template>
