<script setup lang="ts">
import { BlindsGroup } from "@/@types";
import { List, ListHeader, ListItem, ListRoot } from "@/components/ui/shared/list";
import { BlindsSlider } from "@components/shared/blinds-slider";
import BlindsValue from "@components/shared/blinds-value/BlindsValue.vue";
import { BlindsControl } from "@modules/cabin/blinds-control";

import { groupBlindsByGroup } from "@/lib/mappers";
import { isBlindsControl } from "@/lib/utils";
import { useRoomStore } from "@/stores/rooms";
import { computed, ref, toRefs, watch } from "vue";

const { currentRoom, hasPendingRequests } = toRefs(useRoomStore());
const { setBlindsLevel } = useRoomStore();
const selected = ref<BlindsGroup>();

const blinds = computed(() =>
  groupBlindsByGroup(currentRoom.value.roomsControls.filter(isBlindsControl)),
);

watch(currentRoom, (next, prev) => {
  if (next.id !== prev.id) {
    selected.value = undefined;
  }
});
</script>

<template>
  <section
    class="-mx-1.5 flex w-full grow flex-wrap items-center justify-center max-md:pb-[64px] md:px-6 md:pb-[32px]"
    :class="{
      'px-3': blinds.length > 1,
      'px-4 md:px-6': blinds.length === 1,
    }"
  >
    <ListRoot
      v-for="(group, index) in blinds"
      :key="index"
      :class="{
        'w-1/2 px-1.5 xl:w-1/3 landscape:lg:w-1/3': blinds.length > 1,
        'w-full md:w-1/2 xl:w-1/3 landscape:lg:w-1/3':
          group.controls.length === 1 && blinds.length === 1,
        'w-full xl:w-2/3 landscape:lg:w-2/3': group.controls.length === 2 && blinds.length === 1,
      }"
    >
      <ListHeader v-if="blinds.length > 1">{{ group.name }}</ListHeader>
      <List
        orientation="horizontal"
        :size="group.controls.length"
      >
        <ListItem
          v-for="(item, controlIndex) in group.controls"
          :key="item.name!"
          data-testid="blinds-control"
          class="flex-col pb-6"
          @click="selected = group"
        >
          <span
            :class="{
              'text-base font-medium': blinds.length === 1,
              'text-sm': blinds.length > 1,
            }"
          >
            {{ item.name }}</span
          >
          <BlindsSlider
            v-if="blinds.length === 1"
            v-model:level="item.value"
            class="mt-3"
            :disabled="hasPendingRequests"
            @update:level="setBlindsLevel(item.id, $event)"
          />
          <BlindsValue
            v-else
            :level="item.value"
            :color="controlIndex === 0 ? ' bg-primary/90' : 'bg-primary/45'"
          />
        </ListItem>
      </List>
    </ListRoot>

    <BlindsControl
      v-if="blinds.length > 1"
      v-model:group="selected"
    />
  </section>
</template>
