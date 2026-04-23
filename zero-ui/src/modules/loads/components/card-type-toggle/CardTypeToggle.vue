<script setup lang="ts">
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group";
import { cn } from "@/modules/common/lib/utils";
import { RiDashboardLine, RiMenuLine } from "@remixicon/vue";
import type { HTMLAttributes } from "vue";
import { useI18n } from "vue-i18n";
import type { CardType } from "../../types";

const { t } = useI18n();
const props = defineProps<{ class?: HTMLAttributes["class"] }>();

const modelValue = defineModel<CardType>({
  required: true,
});

const onUpdate = (value: CardType | null) => {
  if (value) {
    modelValue.value = value;
  }
};
</script>

<template>
  <ToggleGroup
    :model-value="modelValue"
    type="single"
    variant="outline"
    size="sm"
    :class="cn('ml-2', props.class)"
    @update:model-value="onUpdate"
  >
    <ToggleGroupItem
      value="numerical"
      class="px-2"
      :aria-label="t('loads.components.cardTypeToggle.numerical')"
      :title="t('loads.components.cardTypeToggle.numerical')"
    >
      <RiMenuLine class="size-4" />
      <span class="sr-only">{{ t("loads.components.cardTypeToggle.numerical") }}</span>
    </ToggleGroupItem>
    <ToggleGroupItem
      value="graphical"
      class="px-2"
      :aria-label="t('loads.components.cardTypeToggle.graphical')"
      :title="t('loads.components.cardTypeToggle.graphical')"
    >
      <RiDashboardLine class="size-4" />

      <span class="sr-only">{{ t("loads.components.cardTypeToggle.graphical") }}</span>
    </ToggleGroupItem>
  </ToggleGroup>
</template>
