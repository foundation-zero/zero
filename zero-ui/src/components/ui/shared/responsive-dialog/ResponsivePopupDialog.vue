<script setup lang="ts">
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/shadcn/dialog";

const open = defineModel<boolean>("open", { required: true });
defineProps<{ title: string; description: string }>();
</script>

<template>
  <Dialog
    v-model:open="open"
    modal
    class="p-0"
  >
    <DialogTrigger>
      <slot name="trigger" />
    </DialogTrigger>
    <DialogContent class="max-w-[450px] overflow-hidden">
      <DialogHeader>
        <DialogTitle>{{ title }}</DialogTitle>
        <DialogDescription>{{ description }}</DialogDescription>
      </DialogHeader>

      <slot />
    </DialogContent>
  </Dialog>
</template>
