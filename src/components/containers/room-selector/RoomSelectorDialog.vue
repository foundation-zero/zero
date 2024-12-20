<script setup lang="ts">
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { ref } from "vue";
import { ScrollArea } from "../../ui/scroll-area";
import RoomSelectorButton from "./RoomSelectorButton.vue";
import RoomsList from "./RoomsList.vue";

const isActive = ref(false);
</script>

<template>
  <Dialog
    v-model:open="isActive"
    modal
    class="p-0"
  >
    <DialogTrigger>
      <RoomSelectorButton />
    </DialogTrigger>
    <DialogContent class="max-w-[450px] overflow-hidden">
      <DialogHeader>
        <DialogTitle>ZERO rooms</DialogTitle>
        <DialogDescription>
          Here you can select the room from which you want to operate the household controls
        </DialogDescription>
      </DialogHeader>

      <ScrollArea class="grow w-full portrait:h-[600px] landscape:h-[500px]">
        <RoomsList
          class="py-8"
          @room-selected="isActive = false"
        />
      </ScrollArea>
    </DialogContent>
  </Dialog>
</template>
