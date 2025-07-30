<script setup lang="ts">
import { useRoomStore } from "@/stores/rooms";
import { inject, Ref, toRefs } from "vue";
import SensorStateArea from "./SensorStateArea.vue";

const { areas } = toRefs(useRoomStore());

const showSideNav = inject<Ref<boolean>>("showSideNav");
</script>

<template>
  <article
    class="grid gap-8 pb-8 xl:grid-cols-3"
    :class="{ 'md:grid-cols-2': !showSideNav, 'lg:grid-cols-2': showSideNav }"
  >
    <SensorStateArea
      v-for="area in areas"
      :key="area.name"
      :area="area"
    />
  </article>
</template>
