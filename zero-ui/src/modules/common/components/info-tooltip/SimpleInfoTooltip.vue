<script setup lang="ts">
import { PopoverArrow } from "@/components/ui/popover";
import InfoTooltip from "./InfoTooltip.vue";
import { HTMLAttributes } from "vue";
import { cn } from "../../lib/utils";
import { useTranslations } from "@/modules/thrapp/mimics/tooltips";

const props = defineProps<{
  iconClass?: HTMLAttributes["class"];
  triggerClass?: HTMLAttributes["class"];
  contentClass?: HTMLAttributes["class"];
  description?: string;
}>();

const { descriptions } = useTranslations();
</script>

<template>
  <InfoTooltip
    v-if="!description || descriptions.exists(description)"
    :trigger-class="cn('[&>svg]:size-4', props.triggerClass)"
    :icon-class="cn('fill-brand', props.iconClass)"
    :content-class="
      cn(
        'bg-border-subtle text-foreground w-50 rounded-lg border-none px-3 py-1 text-base leading-8 font-normal shadow-none',
        props.contentClass,
      )
    "
  >
    <slot v-if="description">
      {{ descriptions(description) }}
    </slot>
    <slot v-else />
    <PopoverArrow
      class="fill-border-subtle"
      :width="12"
      :height="4"
    />
  </InfoTooltip>
</template>
