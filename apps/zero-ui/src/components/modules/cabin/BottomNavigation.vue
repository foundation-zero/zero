<script setup lang="ts">
import { useUIStore } from "@/stores/ui";
import { Tabs, TabsList, TabsTrigger } from "@components/shared/bottom-tabs";
import { Blinds, LampCeiling, Snowflake } from "lucide-vue-next";
import { toRefs } from "vue";
import { useI18n } from "vue-i18n";
import { useRoute } from "vue-router";

const { hasScroll, isBottom } = toRefs(useUIStore());
const { name } = toRefs(useRoute());

const { t } = useI18n();
</script>

<template>
  <Tabs
    as="nav"
    :model-value="String(name)"
    class="fixed bottom-0 w-full"
  >
    <div
      class="absolute bottom-0 left-0 right-0 top-0 bg-background transition-all sm:bg-background"
      :class="{ 'border-t': hasScroll && !isBottom }"
    ></div>

    <TabsList class="relative grid grid-cols-3">
      <RouterLink
        :to="{ name: 'cabin:airconditioning' }"
        class="text-center"
      >
        <TabsTrigger value="cabin:airconditioning">
          <Snowflake
            :size="22"
            stroke-width="2"
          />
          {{ t("labels.airconditioning.short") }}
        </TabsTrigger>
      </RouterLink>
      <RouterLink
        :to="{ name: 'cabin:lights' }"
        class="text-center"
      >
        <TabsTrigger value="cabin:lights">
          <LampCeiling
            :size="24"
            stroke-width="2"
          />
          {{ t("labels.lights") }}
        </TabsTrigger>
      </RouterLink>
      <RouterLink
        :to="{ name: 'cabin:blinds' }"
        class="text-center"
      >
        <TabsTrigger value="cabin:blinds">
          <Blinds
            :size="22"
            stroke-width="2"
          />
          {{ t("labels.blinds") }}
        </TabsTrigger>
      </RouterLink>
    </TabsList>
  </Tabs>
</template>
