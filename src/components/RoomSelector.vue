<script setup lang="ts">
import { Room } from "@/@types";
import { Button } from "@/components/ui/button";
import {
  Drawer,
  DrawerClose,
  DrawerContent,
  DrawerDescription,
  DrawerFooter,
  DrawerHeader,
  DrawerTitle,
  DrawerTrigger,
} from "@/components/ui/drawer";
import { useRoomStore } from "@/stores/rooms";
import { useUIStore } from "@/stores/ui";
import { ArrowBigRight, ArrowRight, Check, CircleArrowRight, ShipWheel } from "lucide-vue-next";
import { ref, toRefs } from "vue";
import { ScrollArea } from "./ui/scroll-area";

const { isScrolling } = toRefs(useUIStore());
const { areas, currentRoom } = toRefs(useRoomStore());
const { setRoom } = useRoomStore();
const isActive = ref(false);

const selectRoom = (room: Room) => {
  isActive.value = false;
  setRoom(room);
};
</script>

<template>
  <Drawer v-model:open="isActive">
    <DrawerTrigger as-child>
      <Button
        variant="ghost"
        size="sm"
        class="text-sm font-bold dark:text-gray-100 transition-all px-0 hover:bg-transparent"
        :disabled="isScrolling"
        :class="{
          '!opacity-100': isScrolling,
          disabled: isScrolling,
          'max-sm:ml-[50%]': isScrolling,
          'max-sm:translate-x-[-50%]': isScrolling,
        }"
      >
        <ShipWheel
          stroke-width="2"
          :class="{ 'max-sm:hidden md:opacity-0': isScrolling }"
        />
        {{ currentRoom.name }}</Button
      >
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
          class="grow mx-auto w-full max-w-sm"
          style="height: calc(100svh - 200px)"
        >
          <div class="pb-8 px-6">
            <template
              v-for="area in areas"
              :key="area.name"
            >
              <header class="uppercase text-xs mt-8">{{ area.name }}</header>
              <ul
                class="mt-2 bg-muted rounded-xl py-0 overflow-hidden hover:cursor-pointer grid grid-cols-1 divide-y"
              >
                <li
                  v-for="room in area.rooms"
                  :key="room.name"
                  :class="{
                    'font-bold': currentRoom.name === room.name,
                    'font-light': currentRoom.name !== room.name,
                  }"
                  @click="selectRoom(room)"
                  class="flex p-6 items-center hover:bg-muted-foreground justify-between gap-2 whitespace-nowrap transition-colors disabled:pointer-events-none disabled:opacity-50 h-8 rounded-md text-md"
                >
                  <span>{{ room.name }}</span>
                  <CircleArrowRight v-if="currentRoom.name === room.name" />
                </li>
              </ul>
            </template>
          </div>
        </ScrollArea>
      </div>
    </DrawerContent>
  </Drawer>
</template>
