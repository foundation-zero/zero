<script setup lang="ts">
import { Button } from "@/components/ui/button";
import { ResponsivePopup } from "@/modules/common/components/responsive-dialog";
import { RiAddFill } from "@remixicon/vue";
import { ref } from "vue";
import { useI18n } from "vue-i18n";

const isOpen = ref(false);

const { t } = useI18n();
</script>

<template>
  <ResponsivePopup
    v-model:open="isOpen"
    class="bg-muted max-h-[90vh]! w-screen! max-w-360! px-0 pb-0 sm:w-[95vw]!"
    :title="t('thrapp.labels.legend')"
  >
    <template #title>
      <h2 class="border-b px-4 pb-2 text-left text-2xl font-semibold sm:px-6 md:text-[2rem]">
        {{ t("thrapp.labels.legend") }}
      </h2>
    </template>
    <template #trigger>
      <Button
        variant="default"
        size="sm"
      >
        {{ t("thrapp.labels.showLegend") }}
        <RiAddFill />
      </Button>
    </template>
    <slot />
  </ResponsivePopup>
</template>
