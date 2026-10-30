<script setup lang="ts">
import {
  Drawer,
  DrawerContent,
  DrawerDescription,
  DrawerHeader,
  DrawerTitle,
  DrawerTrigger,
} from "@/components/ui/drawer";
import { HTMLAttributes } from "vue";
import { cn } from "../../lib/utils";
import { VisuallyHidden } from "reka-ui";
import { useI18n } from "vue-i18n";
const open = defineModel<boolean>("open", { required: true });
const props = defineProps<{
  title?: string;
  description?: string;
  class?: HTMLAttributes["class"];
}>();

const { t } = useI18n();
</script>

<template>
  <Drawer
    v-model:open="open"
    :class="cn('mx-0', props.class)"
  >
    <DrawerTrigger as-child>
      <slot name="trigger" />
    </DrawerTrigger>
    <DrawerContent class="mx-1">
      <div class="flex flex-col overflow-y-auto pb-2">
        <DrawerHeader class="px-0">
          <slot name="title">
            <DrawerTitle>
              {{ title }}
            </DrawerTitle>
          </slot>
        </DrawerHeader>
        <VisuallyHidden v-if="!description">
          <DrawerDescription class="mt-1">{{ t("messages.noDescription") }}</DrawerDescription>
        </VisuallyHidden>
        <DrawerDescription v-else>{{ description }}</DrawerDescription>
        <slot />
      </div>
    </DrawerContent>
  </Drawer>
</template>
