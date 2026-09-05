<script setup lang="ts">
import { Button } from "@/components/ui/button";
import InfoTooltip from "@/modules/common/components/info-tooltip/InfoTooltip.vue";
import { ref } from "vue";
import { useI18n } from "vue-i18n";

const { tm, t } = useI18n();
const isOpen = ref(false);
</script>

<template>
  <InfoTooltip
    v-model:open="isOpen"
    icon-class="fill-destructive"
  >
    <template #trigger>
      <span class="text-destructive flex justify-center text-sm">
        {{ t("thrapp.dialogs.advisoryModeDisabled.title") }}
      </span>
    </template>
    <hgroup class="grid max-w-72 gap-4 px-2 py-4">
      <header class="mb-6 text-xl font-bold">
        {{ tm("thrapp.dialogs.advisoryModeDisabled.title") }}
      </header>
      <p
        v-for="(content, index) in tm('thrapp.dialogs.advisoryModeDisabled.content')"
        :key="index"
        class="text-base font-medium"
      >
        {{ content }}
      </p>
      <Button
        variant="secondary"
        class="mt-6"
        @click="isOpen = false"
      >
        {{ t("thrapp.dialogs.advisoryModeDisabled.action") }}
      </Button>
    </hgroup>
  </InfoTooltip>
</template>
