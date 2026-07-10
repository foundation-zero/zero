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
const open = defineModel<boolean>("open", { required: true });
const props = defineProps<{
  title?: string;
  description?: string;
  class?: HTMLAttributes["class"];
}>();
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
          <div class="w-full text-center">
            <slot name="title">
              <DrawerTitle v-if="title">{{ title }}</DrawerTitle>
            </slot>
            <DrawerDescription
              v-if="description"
              class="mt-1"
              >{{ description }}</DrawerDescription
            >
          </div>
        </DrawerHeader>

        <slot />
      </div>
    </DrawerContent>
  </Drawer>
</template>
