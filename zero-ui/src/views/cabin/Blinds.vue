<script setup lang="ts">
import { BlindsGroup } from "@/@types";
import BlindsControl from "@/components/ui/shared/blinds-slider/BlindsControl.vue";
import BlindsControlPopup from "@/components/ui/shared/blinds-slider/BlindsControlPopup.vue";
import BlindsLabel from "@/components/ui/shared/blinds-slider/BlindsLabel.vue";
import BlindsList from "@/components/ui/shared/blinds-slider/BlindsList.vue";
import BlindsSlider from "@/components/ui/shared/blinds-slider/BlindsSlider.vue";
import List from "@/components/ui/shared/list/List.vue";
import ListHeader from "@/components/ui/shared/list/ListHeader.vue";
import ListItem from "@/components/ui/shared/list/ListItem.vue";
import ListRoot from "@/components/ui/shared/list/ListRoot.vue";

import { groupBlindsByGroup } from "@/lib/mappers";
import { isBlindsControl } from "@/lib/utils";
import { useRoomStore } from "@/stores/rooms";
import { useUIStore } from "@/stores/ui";
import { computed, ref, toRefs, watch } from "vue";

const { currentRoom } = toRefs(useRoomStore());
const { breakpoints } = toRefs(useUIStore());
const selected = ref<BlindsGroup>();

const blinds = computed(() =>
  groupBlindsByGroup(currentRoom.value.roomsControls.filter(isBlindsControl)),
);

watch(currentRoom, (next, prev) => {
  if (next.id !== prev.id) {
    selected.value = undefined;
  }
});

const setGroup = (group: BlindsGroup) => {
  if (selected.value !== group) {
    selected.value = group;
  }
};
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
    <BlindsControlPopup v-model:group="selected" />
  </section>
</template>
