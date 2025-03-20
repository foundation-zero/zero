<script setup lang="ts">
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Blinds, LampCeiling, Snowflake } from "lucide-vue-next";
import { toRefs } from "vue";
import { useI18n } from "vue-i18n";
import { useRoute } from "vue-router";
const { path } = toRefs(useRoute());
const { t } = useI18n();
</script>

<template>
  <Tabs
    :model-value="path"
    class="absolute left-[50%] translate-x-[-50%] max-md:hidden"
  >
    <TabsList
      class="bg-black !bg-opacity-5 backdrop-blur-md dark:bg-white"
      as="nav"
    >
      <RouterLink to="/airco">
        <TabsTrigger value="/airco">
          <Snowflake
            :size="16"
            stroke-width="2"
            class="mr-2 inline"
          />
          {{ t("labels.airconditioning") }}
        </TabsTrigger>
      </RouterLink>
      <RouterLink to="/lights">
        <TabsTrigger value="/lights">
          <LampCeiling
            :size="16"
            stroke-width="2"
            class="mr-2 inline"
          />
          {{ t("labels.lights") }}
        </TabsTrigger>
      </RouterLink>
      <RouterLink to="/blinds">
        <TabsTrigger value="/blinds">
          <Blinds
            :size="16"
            stroke-width="2"
            class="mr-2 inline"
          />
          {{ t("labels.blinds") }}
        </TabsTrigger>
      </RouterLink>
    </TabsList>
  </Tabs>
</template>
