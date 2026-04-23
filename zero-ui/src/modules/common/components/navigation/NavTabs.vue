<script setup lang="ts">
import { Tabs, TabsList, TabsTrigger } from "@common/components/tab-links";
import { toRefs } from "vue";
import { useI18n } from "vue-i18n";
import { useRoute } from "vue-router";
import { getRootRoute } from "../../router";
import { NavItem } from "../../types";
import RouterLinkWithFallback from "../RouterLinkWithFallback.vue";

const { name } = toRefs(useRoute());
defineProps<{ items: NavItem[] }>();

const { t } = useI18n();
</script>

<template>
  <Tabs
    :model-value="getRootRoute(name?.toString())"
    data-testid="main-nav"
  >
    <TabsList
      as="nav"
      class="py-0"
    >
      <RouterLinkWithFallback
        v-for="item in items"
        :key="item.title"
        :to="{ name: item.to }"
      >
        <TabsTrigger :value="getRootRoute(item.to)">
          {{ t(item.title) }}
        </TabsTrigger>
      </RouterLinkWithFallback>
    </TabsList>
  </Tabs>
</template>
