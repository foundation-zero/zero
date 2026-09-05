<script setup lang="ts">
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { HTMLAttributes } from "vue";
import { cn } from "../../lib/utils";
import { InfoIcon } from "../icons";

const props = defineProps<{ iconClass?: HTMLAttributes["class"] }>();
const isOpen = defineModel<boolean>("open", { default: false });
</script>

<template>
  <TooltipProvider>
    <Tooltip
      v-model:open="isOpen"
      :delay-duration="300"
    >
      <TooltipTrigger as-child>
        <button
          type="button"
          class="flex cursor-pointer gap-1"
        >
          <slot name="trigger" />
          <InfoIcon :icon-class="cn('size-5', props.iconClass)" />
        </button>
      </TooltipTrigger>
      <TooltipContent side="bottom">
        <slot />
      </TooltipContent>
    </Tooltip>
  </TooltipProvider>
</template>
