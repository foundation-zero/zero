<script setup lang="ts">
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { HTMLAttributes } from "vue";
import { cn } from "../../lib/utils";
import { VisuallyHidden } from "reka-ui";
import { useI18n } from "vue-i18n";

const open = defineModel<boolean>("open", { required: true });
const props = defineProps<{
  title?: string;
  description?: string;
  maxWidth?: string;
  class?: HTMLAttributes["class"];
}>();
const { t } = useI18n();
</script>

<template>
  <Dialog
    v-model:open="open"
    class="p-0"
  >
    <DialogTrigger>
      <slot name="trigger" />
    </DialogTrigger>
    <DialogContent :class="cn('gap-0 overflow-y-hidden', props.class)">
      <DialogHeader>
        <slot name="title">
          <DialogTitle>
            {{ title }}
          </DialogTitle>
        </slot>
        <VisuallyHidden v-if="!description">
          <DialogDescription>{{ t("messages.noDescription") }}</DialogDescription>
        </VisuallyHidden>
        <DialogDescription v-else>{{ description }}</DialogDescription>
      </DialogHeader>

      <div class="max-h-[80vh] overflow-y-auto px-4 py-4 sm:px-6 sm:py-6">
        <slot />
      </div>
    </DialogContent>
  </Dialog>
</template>
