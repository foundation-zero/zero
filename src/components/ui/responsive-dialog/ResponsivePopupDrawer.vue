<script setup lang="ts">
import {
  Drawer,
  DrawerContent,
  DrawerDescription,
  DrawerHeader,
  DrawerTitle,
  DrawerTrigger,
} from "@/components/ui/drawer";
const open = defineModel<boolean>("open", { required: true });
defineProps<{ title: string; description: string }>();
</script>

<template>
  <Drawer v-model:open="open">
    <DrawerTrigger as-child>
      <slot name="trigger" />
    </DrawerTrigger>
    <DrawerContent>
      <div class="flex flex-col">
        <DrawerHeader class="">
          <div class="mx-auto w-full max-w-sm text-center">
            <DrawerTitle>{{ title }}</DrawerTitle>
            <DrawerDescription class="mt-1">{{ description }}</DrawerDescription>
          </div>
        </DrawerHeader>

        <slot />
      </div>
    </DrawerContent>
  </Drawer>
</template>
