<script setup lang="ts">
import {
  BlindsControl,
  BlindsControlPopup,
  BlindsLabel,
  BlindsList,
  BlindsSlider,
} from "@/modules/domestic/cabin/components/ui/blinds-slider";
import { BlindsGroup } from "@/modules/domestic/types";
import { List, ListHeader, ListItem, ListRoot } from "@common/components/list";

import { groupBlindsByGroup } from "@/modules/domestic/lib/mappers";
import { useRoomStore } from "@/modules/domestic/stores/rooms";
import { useUIStore } from "@common/stores/ui";
import { computed, ref, toRefs, watch } from "vue";

const { currentRoom } = toRefs(useRoomStore());
const { breakpoints } = toRefs(useUIStore());
const selectedGroup = ref<string | undefined>();

const blinds = computed(() => groupBlindsByGroup(currentRoom.value.blinds));

watch(currentRoom, (next, prev) => {
  if (next.id !== prev.id) {
    selectedGroup.value = undefined;
  }
});

const setGroup = (group: BlindsGroup) => {
  if (selectedGroup.value !== group.name) {
    selectedGroup.value = group.name;
  }
};

const selected = computed(() => {
  if (selectedGroup.value) {
    return blinds.value.find((group) => group.name === selectedGroup.value);
  } else {
    return undefined;
  }
});
</script>

<template>
  <section
    v-if="blinds.length === 1"
    class="flex w-full grow items-center justify-center max-md:pb-[96px] md:pb-[32px]"
  >
    <BlindsList
      class="w-full"
      editable
      :group="blinds[0]"
    />
  </section>
  <section
    v-else
    class="grid grid-cols-1 gap-6 px-4 max-md:pb-[96px] md:grid-cols-2 md:px-6 md:pb-[32px] xl:grid-cols-3 landscape:lg:grid-cols-3"
    :class="{
      'max-xl:w-full xl:container xl:px-0': !breakpoints.touch,
      'w-full': breakpoints.touch,
    }"
  >
    <ListRoot
      v-for="group in blinds"
      :key="group.name"
    >
      <ListHeader>{{ group.name }}</ListHeader>
      <List
        orientation="horizontal"
        :size="group.controls.length"
        class="hover:border-brand/60 hover:border"
        @click="setGroup(group)"
      >
        <ListItem
          v-for="control in group.controls"
          :key="control.id"
          class="cursor-pointer justify-around px-0 py-6"
        >
          <BlindsControl
            :control="control"
            class="w-1/3"
            :class="{
              'max-md:text-5xl md:text-6xl': group.controls.length === 1,
              'max-md:text-3xl md:text-4xl': group.controls.length === 2,
            }"
          >
            <BlindsSlider @click="setGroup(group)" />
            <BlindsLabel v-if="group.controls.length > 1" />
          </BlindsControl>
        </ListItem>
      </List>
    </ListRoot>
    <BlindsControlPopup :group="selected" />
  </section>
</template>
