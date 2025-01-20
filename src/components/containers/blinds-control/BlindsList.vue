<script setup lang="ts">
import { BlindsGroup } from "@/@types";
import { BlindsSlider } from "@/components/ui/blinds-slider";
import { List, ListItem } from "@/components/ui/list";

defineProps<{ group: BlindsGroup }>();
</script>

<template>
  <List
    orientation="horizontal"
    :size="group.controls.length"
  >
    <ListItem
      v-for="item in group.controls"
      :key="item.name"
      class="flex-col pb-6"
    >
      <span class="text-lg font-medium"> {{ item.name }}</span>
      <BlindsSlider
        v-model:position="item.position"
        class="mt-3"
        @touchstart.stop.prevent
        @mousedown.stop.prevent
      />
    </ListItem>
  </List>
</template>
