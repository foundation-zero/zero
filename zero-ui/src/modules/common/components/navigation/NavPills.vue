<script setup lang="ts">
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { toRefs } from "vue";
import { useI18n } from "vue-i18n";
import { useRoute } from "vue-router";
import { NavItem } from "../../types";
import RouterLinkWithFallback from "../RouterLinkWithFallback.vue";

defineProps<{ items: NavItem[] }>();

const { name } = toRefs(useRoute());

const { t } = useI18n();
</script>

<template>
  <Tabs
    :model-value="name?.toString()"
    data-testid="sub-nav"
  >
    <TabsList as="nav">
      <RouterLinkWithFallback
        v-for="item in items"
        :key="item.title"
        :to="{ name: item.to }"
      >
        <TabsTrigger :value="item.to">
          {{ t(item.title) }}
        </TabsTrigger>
      </RouterLinkWithFallback>
    </TabsList>
  </Tabs>
</template>
