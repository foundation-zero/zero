<script setup lang="ts">
import { Tabs, TabsList, TabsTrigger } from "@common/components/bottom-tabs";
import { useUIStore } from "@common/stores/ui";
import { Snowflake } from "lucide-vue-next";
import { toRefs } from "vue";
import { useI18n } from "vue-i18n";
import { useRoute } from "vue-router";
import { NavItem } from "../../types";

defineProps<{ items: NavItem[] }>();

const { hasScroll, isBottom } = toRefs(useUIStore());
const { name } = toRefs(useRoute());

const { t } = useI18n();
</script>

<template>
  <Tabs
    as="nav"
    :model-value="String(name)"
    class="fixed bottom-0 w-full sm:hidden"
  >
    <div
      class="bg-background/80 sm:bg-background absolute top-0 right-0 bottom-0 left-0 backdrop-blur-md transition-all"
      :class="{ 'border-t': hasScroll && !isBottom }"
    ></div>

    <TabsList class="relative grid grid-cols-3">
      <RouterLink
        v-for="item in items"
        :key="item.title"
        :to="{ name: item.to }"
        class="text-center"
      >
        <TabsTrigger :value="item.to">
          <Snowflake
            :size="22"
            stroke-width="2"
          />
          {{ t(item.title) }}
        </TabsTrigger>
      </RouterLink>
    </TabsList>
  </Tabs>
</template>
