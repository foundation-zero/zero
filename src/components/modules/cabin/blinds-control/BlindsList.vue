<script setup lang="ts">
import { BlindsGroup } from "@/@types";
import { useRoomStore } from "@/stores/rooms";
import { List, ListItem } from "@components/shadcn/list";
import { BlindsSlider } from "@components/shared/blinds-slider";

defineProps<{ group: BlindsGroup }>();

const { setBlindsLevel } = useRoomStore();
</script>

<template>
  <List
    orientation="horizontal"
    :size="group.controls.length"
  >
    <ListItem
      v-for="item in group.controls"
      :key="item.name!"
      class="flex-col pb-6"
    >
      <span class="text-lg font-medium"> {{ item.name }}</span>
      <BlindsSlider
        v-model:level="item.value"
        class="mt-3"
        @update:level="setBlindsLevel(item.id, $event)"
        @touchstart.stop.prevent
        @mousedown.stop.prevent
      />
    </ListItem>
  </List>
</template>
