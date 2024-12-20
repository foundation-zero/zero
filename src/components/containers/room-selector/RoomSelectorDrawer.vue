<script setup lang="ts">
import {
  Drawer,
  DrawerContent,
  DrawerDescription,
  DrawerHeader,
  DrawerTitle,
  DrawerTrigger,
} from "@/components/ui/drawer";
import { ref } from "vue";
import { ScrollArea } from "../../ui/scroll-area";
import RoomSelectorButton from "./RoomSelectorButton.vue";
import RoomsList from "./RoomsList.vue";

const isActive = ref(false);
</script>

<template>
  <Drawer v-model:open="isActive">
    <DrawerTrigger as-child>
      <RoomSelectorButton />
    </DrawerTrigger>
    <DrawerContent>
      <div class="flex flex-col">
        <DrawerHeader class="dark:border-b shadow-sm dark:shadow-none">
          <div class="mx-auto w-full max-w-sm text-center">
            <DrawerTitle>ZERO rooms</DrawerTitle>
            <DrawerDescription class="mt-1"
              >Here you can select the room from which you want to operate the household
              controls</DrawerDescription
            >
          </div>
        </DrawerHeader>

        <ScrollArea
          class="grow w-full"
          style="height: calc(100svh - 200px)"
        >
          <RoomsList
            class="py-8 px-6"
            @room-selected="isActive = false"
          />
        </ScrollArea>
      </div>
    </DrawerContent>
  </Drawer>
</template>
