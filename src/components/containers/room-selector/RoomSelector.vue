<script setup lang="ts">
import { ResponsivePopup } from "@/components/ui/responsive-dialog";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useUIStore } from "@/stores/ui";
import { ref, toRefs } from "vue";
import RoomSelectorButton from "./RoomSelectorButton.vue";
import RoomsList from "./RoomsList.vue";

const isOpen = ref(false);
const { breakpoints } = toRefs(useUIStore());

const { setScrollPosition } = useUIStore();
const { scrollPositions } = toRefs(useUIStore());
</script>

<template>
  <ResponsivePopup
    v-model:open="isOpen"
    title="ZERO rooms"
    description="Here you can select the room from which you want to operate the household controls"
  >
    <template #trigger><RoomSelectorButton /></template>
    <ScrollArea
      ref="scroll"
      :scroll-position="scrollPositions['rooms']"
      class="w-full grow"
      :class="{
        'portrait:h-[600px] landscape:h-[500px]': !breakpoints.phone,
        'h-[calc(100svh-200px)]': breakpoints.phone,
      }"
      @scroll-y="(val) => setScrollPosition('rooms', val)"
    >
      <RoomsList
        class="py-8"
        :class="{ 'px-6': breakpoints.phone }"
        @room-selected="isOpen = false"
      />
    </ScrollArea>
  </ResponsivePopup>
</template>
