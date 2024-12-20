<script setup lang="ts">
import { Button } from "@/components/ui/button";

import { useRoomStore } from "@/stores/rooms";
import { useUIStore } from "@/stores/ui";
import { ShipWheel } from "lucide-vue-next";
import { toRefs } from "vue";

const { isScrolling } = toRefs(useUIStore());
const { currentRoom } = toRefs(useRoomStore());
</script>

<template>
  <Button
    variant="ghost"
    size="sm"
    class="text-sm font-bold dark:text-gray-100 transition-all px-0 hover:bg-transparent"
    :disabled="isScrolling"
    :class="{
      '!opacity-100 disabled max-sm:ml-[50%] landscape:max-md:ml-[50%] landscape:max-md:translate-x-[-50%] max-sm:translate-x-[-50%]':
        isScrolling,
    }"
  >
    <ShipWheel
      stroke-width="2"
      :class="{ 'max-sm:hidden md:opacity-0': isScrolling }"
    />
    {{ currentRoom.name }}</Button
  >
</template>
