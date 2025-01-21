<script setup lang="ts">
import { BlindsGroup } from "@/@types";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import BlindsList from "./BlindsList.vue";

const open = defineModel<boolean>("open");
defineProps<{ group: BlindsGroup }>();
</script>

<template>
  <Dialog
    v-model:open="open"
    modal
    class="p-0"
  >
    <DialogContent class="max-w-[450px] overflow-hidden">
      <DialogHeader>
        <DialogTitle>{{ group.name }}</DialogTitle>
        <DialogDescription> Control the blinds and sheers </DialogDescription>
      </DialogHeader>

      <BlindsList
        :group="group"
        class="w-full"
      />
    </DialogContent>
  </Dialog>
</template>
