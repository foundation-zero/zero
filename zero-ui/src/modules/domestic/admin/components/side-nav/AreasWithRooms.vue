<script setup lang="ts">
import CabinLayout from "@/modules/domestic/cabin/layouts/DefaultLayout.vue";
import { ShipArea } from "@/modules/domestic/types";
import { Collapsible } from "@common/components/collapsible";
import { NavList, NavListItem } from "@common/components/nav-list";
import { computed, toRefs } from "vue";
import { useRoute } from "vue-router";

defineProps<{ areas: ShipArea[]; currentRoomId: string }>();

const route = toRefs(useRoute());

const isCabinView = computed(() =>
  route.matched.value.some((item) => item.meta.layout === CabinLayout),
);
</script>

<template>
  <Collapsible
    v-for="area in areas"
    :key="area.name"
    :title="area.name"
    :open="area.rooms.some((room) => room.id === currentRoomId)"
  >
    <NavList role="list">
      <NavListItem
        v-for="room in area.rooms"
        :key="room.id"
        :to="{
          name: isCabinView ? route.name.value : 'cabin:airconditioning',
          query: { room: room.id },
        }"
        :data-testid="`room-${room.id}`"
        :active="isCabinView && room.id === currentRoomId"
      >
        <span>{{ room.name }}</span>
      </NavListItem>
    </NavList>
  </Collapsible>
</template>
