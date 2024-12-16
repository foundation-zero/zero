<script setup lang="ts">
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useUIStore } from "@/stores/ui";
import { Blinds, LampCeiling, Snowflake } from "lucide-vue-next";
import { toRefs } from "vue";
import { useRoute } from "vue-router";
const { isScrolling } = toRefs(useUIStore());

const { path } = toRefs(useRoute());
</script>

<template>
  <Tabs
    :model-value="path"
    class="fixed top-0 w-full container transition-all"
    :class="{
      'pt-5': !isScrolling,
      'max-sm:py-1 md:pt-1 max-sm:shadow-md max-sm:bg-background dark:border-b': isScrolling,
    }"
  >
    <div class="flex flex-row items-center transition-all justify-between">
      <div
        class="grow transition-opacity"
        :class="{ 'md:opacity-0': isScrolling }"
      >
        <slot name="left"> </slot>
      </div>

      <div class="grow max-sm:hidden">
        <TabsList class="backdrop-blur-xl bg-gray-100 dark:bg-gray-900 bg-opacity-80">
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
      </div>

      <div
        class="grow items-end flex flex-row justify-end transition-opacity"
        :class="{ 'md:opacity-0': isScrolling, 'max-sm:hidden': isScrolling }"
      >
        <slot name="right"> </slot>
      </div>
    </div>
  </Tabs>
</template>
