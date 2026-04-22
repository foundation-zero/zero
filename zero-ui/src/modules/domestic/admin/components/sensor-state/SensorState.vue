<script setup lang="ts">
import { useRoomStore } from "@/modules/domestic/stores/rooms";
import { toRefs } from "vue";
import SensorStateArea from "./SensorStateArea.vue";

const { areas } = toRefs(useRoomStore());
</script>

<template>
  <article class="grid gap-8 pb-8 md:grid-cols-2 xl:grid-cols-3">
    <SensorStateArea
      v-for="area in areas"
      :key="area.name"
      :area="area"
    />
  </article>
</template>
