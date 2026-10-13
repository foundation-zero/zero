<script setup lang="ts">
import { RiTimeLine } from "@remixicon/vue";
import { HTMLAttributes } from "vue";
import { useI18n } from "vue-i18n";
import { FieldRenderer } from "../../renderers";
import ValueListItem from "./ValueListItem.vue";

const props = defineProps<{ value?: number; class?: HTMLAttributes["class"] }>();

const { t } = useI18n();
</script>

<template>
  <ValueListItem :class="props.class">
    <span class="flex items-center gap-0.5">
      <RiTimeLine class="text-attention-dull size-3.5" />
      {{ t("units.estimatedTime") }}
    </span>
    <span class="text-foreground font-medium">
      <FieldRenderer.TimeRemaining :value="value" />
    </span>
  </ValueListItem>
</template>
