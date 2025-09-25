<script setup lang="ts">
import Breadcrumbs from "@/components/modules/thrs/Breadcrumbs.vue";
import NavPills from "@/components/modules/thrs/NavPills.vue";
import Toolbar from "@/components/modules/thrs/Toolbar.vue";
import ToolbarActions from "@/components/modules/thrs/ToolbarActions.vue";
import { useI18n } from "vue-i18n";

const { t } = useI18n();
</script>

<template>
  <main class="container mx-auto h-svh px-3 pt-[96px]">
    <slot></slot>
  </main>
  <nav class="fixed top-0 right-0 left-0">
    <Toolbar class="py-1 pr-2 pl-3">
      <template #left>
        <h4 class="text-2xl font-semibold uppercase">{{ t("labels.thrs") }}</h4>
      </template>
      <template #center>
        <NavPills />
      </template>
      <template #right>
        <ToolbarActions />
      </template>
    </Toolbar>
    <Toolbar class="py-1 pr-2 pl-3">
      <template #left><Breadcrumbs /></template>
      <template #center> </template>
    </Toolbar>
  </nav>
</template>
