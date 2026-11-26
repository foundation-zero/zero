<script setup lang="ts">
import TopNavAppLogo from "@/modules/common/components/navigation/TopNavAppLogo.vue";
import { useI18n } from "vue-i18n";

const { t } = useI18n();
</script>

<template>
  <RouterLink
    :to="{ name: 'thrs' }"
    class="focus-visible:ring-brand font-headers rounded-sm outline-none focus-visible:ring-2"
  >
    <TopNavAppLogo
      class="gap-1.5 max-sm:flex"
      suffix-class="text-brand"
    >
      - {{ t("apps.thrs") }}
    </TopNavAppLogo>
  </RouterLink>
</template>
