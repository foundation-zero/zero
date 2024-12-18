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
    class="fixed top-0 transition-all w-full"
    :class="{
      'pt-5': !isScrolling,
      'max-sm:py-1 md:pt-2 max-sm:shadow-sm max-sm:bg-background max-md:dark:border-b': isScrolling,
    }"
  >
    <div class="flex flex-row container items-center transition-all justify-between relative">
      <div
        class="transition-opacity grow"
        :class="{ 'md:opacity-0': isScrolling }"
      >
        <slot name="left"> </slot>
      </div>

      <div class="absolute left-[50%] translate-x-[-50%] max-md:hidden">
        <TabsList class="bg-black dark:bg-white !bg-opacity-5 backdrop-blur-md">
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
        class="items-end flex flex-row justify-end transition-opacity grow"
        :class="{ 'md:opacity-0': isScrolling, 'max-sm:hidden': isScrolling }"
      >
        <slot name="right"> </slot>
      </div>
    </div>
  </Tabs>
</template>
