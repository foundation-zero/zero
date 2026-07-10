<script setup lang="ts">
import { HTMLAttributes } from "vue";
import { useI18n } from "vue-i18n";
import { cn } from "../../lib/utils";

const { t } = useI18n();

const props = withDefaults(
  defineProps<{
    class?: HTMLAttributes["class"];
    tag?: keyof HTMLElementTagNameMap;
  }>(),
  {
    tag: "span",
  },
);
</script>

<template>
  <component
    :is="props.tag"
    ref="title"
    :class="cn('tracking-ultrawide text-center font-bold uppercase', props.class)"
  >
    {{ t("app.title") }}
  </component>
</template>
