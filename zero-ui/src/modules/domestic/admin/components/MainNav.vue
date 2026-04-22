<script setup lang="ts">
import { TopNavToolbar } from "@/modules/common/components/navigation";
import NavTabs from "@/modules/common/components/navigation/NavTabs.vue";

import TopNavAppLogo from "@/modules/common/components/navigation/TopNavAppLogo.vue";

import { NavItem } from "@/modules/common/types";
import { useI18n } from "vue-i18n";

const { t } = useI18n();

const navItems: NavItem[] = [{ title: "labels.cabins", to: "environment:control" }];
</script>

<template>
  <TopNavToolbar>
    <template #left-content>
      <TopNavAppLogo>{{ t("apps.domestic") }}</TopNavAppLogo>

      <NavTabs
        :items="navItems"
        class="md:ml-12"
      />
    </template>
  </TopNavToolbar>
</template>
