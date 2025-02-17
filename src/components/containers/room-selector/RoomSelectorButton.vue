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
    class="px-0 text-sm font-bold transition-all hover:bg-transparent dark:text-gray-100"
    :disabled="isScrolling"
    :class="{
      'disabled !opacity-100 max-sm:ml-[50%] max-sm:translate-x-[-50%] landscape:max-md:ml-[50%] landscape:max-md:translate-x-[-50%]':
        isScrolling,
    }"
  >
    <ShipWheel
      stroke-width="2"
      :class="{ 'max-sm:hidden md:opacity-0': isScrolling }"
    />
    {{ currentRoom?.name ?? "" }}</Button
  >
</template>
