<script setup lang="ts">
import { useI18n } from "vue-i18n";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { HTMLAttributes } from "vue";
import { cn } from "../../lib/utils";
import { ZiInfoIcon } from "../icons";

const props = defineProps<{ iconClass?: HTMLAttributes["class"] }>();
const isOpen = defineModel<boolean>("open", { default: false });

const { t } = useI18n();
</script>

<template>
  <Popover v-model:open="isOpen">
    <PopoverTrigger as-child>
      <button
        type="button"
        class="flex cursor-pointer gap-1"
        :aria-label="t('labels.moreInformation')"
      >
        <slot name="trigger" />
        <ZiInfoIcon :icon-class="cn('size-5', props.iconClass)" />
      </button>
    </PopoverTrigger>
    <PopoverContent side="bottom">
      <slot />
    </PopoverContent>
  </Popover>
</template>
