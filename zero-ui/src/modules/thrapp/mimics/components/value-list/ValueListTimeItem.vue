<script setup lang="ts">
import AnimatedNumber from "@/modules/loads/components/animated-number/AnimatedNumber.vue";
import { RiTimeLine } from "@remixicon/vue";
import { computed, HTMLAttributes } from "vue";
import { useI18n } from "vue-i18n";
import ValueListItem from "./ValueListItem.vue";

const props = defineProps<{ value?: number; class?: HTMLAttributes["class"] }>();

const { t } = useI18n();

const minutes = computed(() =>
  props.value === undefined ? undefined : Math.floor(props.value / 60),
);

const seconds = computed(() => (props.value === undefined ? undefined : props.value % 60));
</script>

<template>
  <ValueListItem :class="props.class">
    <span class="flex items-center gap-0.5">
      <RiTimeLine class="text-attention-dull size-3.5" />
      {{ t("units.estimatedTime") }}
    </span>
    <span class="text-foreground font-medium">
      <AnimatedNumber
        :to="minutes"
        :fraction-digits="0"
      />
      {{ t("units.minutes") }}
      <AnimatedNumber
        :to="seconds"
        :fraction-digits="0"
      />
      {{ t("units.seconds") }}
    </span>
  </ValueListItem>
</template>
