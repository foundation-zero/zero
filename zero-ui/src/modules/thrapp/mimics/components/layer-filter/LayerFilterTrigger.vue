<script setup lang="ts">
import { Button } from "@/components/ui/button";
import { ResponsivePopup } from "@/modules/common/components/responsive-dialog";
import ResponsivePopupTitle from "@/modules/common/components/responsive-dialog/ResponsivePopupTitle.vue";
import { useUIStore } from "@/modules/common/stores/ui";
import { RiAddFill } from "@remixicon/vue";
import { storeToRefs } from "pinia";
import { ref } from "vue";
import { useI18n } from "vue-i18n";
import { LayerFilterOption } from "./layer-filter.provider";
import LayerFilterOptions from "./LayerFilterOptions.vue";

defineProps<{ options: LayerFilterOption[] }>();

const isOpen = ref(false);

const { t } = useI18n();
const { breakpoints } = storeToRefs(useUIStore());
</script>

<template>
  <ResponsivePopup
    v-model:open="isOpen"
    class="px-0 pb-0 sm:max-w-sm"
  >
    <template #title>
      <ResponsivePopupTitle class="border-b px-4 pb-2 text-left sm:px-6">
        {{ t("thrapp.labels.view") }}
      </ResponsivePopupTitle>
    </template>
    <template #trigger>
      <Button
        variant="default"
        size="sm"
      >
        {{ t("thrapp.labels.view") }}
        <RiAddFill />
      </Button>
    </template>
    <!-- Unlike the dialog, the drawer doesn't pad its content. -->
    <LayerFilterOptions
      :class="{ 'p-4': breakpoints.phone }"
      :options="options"
    />
  </ResponsivePopup>
</template>
