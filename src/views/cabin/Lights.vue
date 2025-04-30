<script setup lang="ts">
import LightGroup from "@/components/ui/lights-list/LightGroup.vue";
import { useRoomStore } from "@/stores/rooms";
import { useUIStore } from "@/stores/ui";
import { toRefs } from "vue";

const { currentRoom, hasPendingRequests } = toRefs(useRoomStore());
const { breakpoints } = toRefs(useUIStore());
const { setLightLevel } = useRoomStore();
</script>

<template>
  <section
    class="grid grid-cols-1 gap-6 px-4 max-md:pb-[96px] md:grid-cols-2 md:px-6 md:pb-[32px] xl:grid-cols-3 landscape:lg:grid-cols-3"
    :class="{
      'xl:container max-xl:w-full xl:px-0': !breakpoints.touch,
      'w-full': breakpoints.touch,
    }"
  >
    <LightGroup
      v-for="(group, index) in currentRoom.lights"
      :key="index"
      :disabled="hasPendingRequests"
      :name="group.name"
      :lights="group.controls"
      @update:level="setLightLevel($event.id, $event.level)"
    />
  </section>
</template>
