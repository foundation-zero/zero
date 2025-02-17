<script setup lang="ts">
import { BlindsGroup } from "@/@types";
import { BlindsControl } from "@/components/containers/blinds-control";
import { BlindsSlider } from "@/components/ui/blinds-slider";
import BlindsValue from "@/components/ui/blinds-value/BlindsValue.vue";
import { List, ListHeader, ListItem, ListRoot } from "@/components/ui/list";

import { useRoomStore } from "@/stores/rooms";
import { ref, toRefs, watch } from "vue";

const { currentRoom } = toRefs(useRoomStore());
const selected = ref<BlindsGroup>();

watch(currentRoom, (next, prev) => {
  if (next !== prev) {
    selected.value = undefined;
  }
});
</script>

<template>
  <section
    class="container flex grow flex-wrap items-center justify-center max-md:pb-[64px] md:px-6 md:pb-[32px]"
    :class="{ 'px-3': currentRoom.blinds.length > 1, 'px-6': currentRoom.blinds.length === 1 }"
  >
    <ListRoot
      v-for="(group, index) in currentRoom.blinds"
      :key="index"
      class="md:px-3"
      :class="{
        'w-1/2 px-1.5 xl:w-1/3 landscape:lg:w-1/3': currentRoom.blinds.length > 1,
        'w-full md:w-1/2 xl:w-1/3 landscape:lg:w-1/3':
          group.controls.length === 1 && currentRoom.blinds.length === 1,
        'w-full xl:w-2/3 landscape:lg:w-2/3':
          group.controls.length === 2 && currentRoom.blinds.length === 1,
      }"
    >
      <ListHeader v-if="currentRoom.blinds.length > 1">{{ group.name }}</ListHeader>
      <List
        orientation="horizontal"
        :size="group.controls.length"
      >
        <ListItem
          v-for="(item, controlIndex) in group.controls"
          :key="item.name!"
          class="flex-col pb-6"
          @click="selected = group"
        >
          <span
            :class="{
              'text-base font-medium': currentRoom.blinds.length === 1,
              'text-sm': currentRoom.blinds.length > 1,
            }"
          >
            {{ item.name }}</span
          >
          <BlindsSlider
            v-if="currentRoom.blinds.length === 1"
            v-model:level="item.level"
            class="mt-3"
          />
          <BlindsValue
            v-else
            :level="item.level"
            :color="controlIndex === 0 ? ' bg-primary/90' : 'bg-primary/45'"
          />
        </ListItem>
      </List>
    </ListRoot>

    <BlindsControl
      v-if="currentRoom.blinds.length > 1"
      v-model:group="selected"
    />
  </section>
</template>
