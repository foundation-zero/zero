<script lang="ts" setup>
import { cn } from "@common/lib/utils";
import { RiMoreLine } from "@remixicon/vue";
import type { HTMLAttributes } from "vue";
import { useI18n } from "vue-i18n";

const props = defineProps<{
  class?: HTMLAttributes["class"];
}>();

const { t } = useI18n();
</script>

<template>
  <span
    data-slot="breadcrumb-ellipsis"
    role="presentation"
    aria-hidden="true"
    :class="cn('flex size-9 items-center justify-center', props.class)"
  >
    <slot>
      <RiMoreLine class="size-4" />
    </slot>
    <span class="sr-only">{{ t("labels.more") }}</span>
  </span>
</template>
