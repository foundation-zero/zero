<script setup lang="ts">
import { useI18n } from "vue-i18n";
import { useRoute } from "vue-router";

const { t } = useI18n();

// Menu items.
const menuItems = [
  {
    title: t("views.thrs.hmi.controls"),
    to: "thrs/hmi/controls",
  },
  {
    title: t("views.thrs.hmi.parameters"),
    to: "thrs/hmi/parameters",
  },
  {
    title: t("views.thrs.hmi.simulation"),
    to: "thrs/hmi/simulation",
  },
  {
    title: t("views.thrs.hmi.sensors"),
    to: "thrs/hmi/sensors",
  },
];

const route = useRoute();
</script>

<template>
  <ul class="grid gap-1 text-lg font-light">
    <RouterLink
      v-for="item in menuItems"
      :key="item.title"
      :to="{ name: item.to }"
    >
      <li
        class="hover:bg-accent hover:text-accent-foreground flex cursor-pointer items-center gap-2 rounded-md px-4 py-2 transition-all"
        :class="{ 'text-accent-foreground font-medium': route.name === item.to }"
      >
        {{ item.title }}
      </li>
    </RouterLink>
  </ul>
</template>
