<script setup lang="ts">
import { Table, TableBody } from "@/components/ui/table";
import { RoomWithState, ShipArea } from "@/modules/domestic/types";
import { compareByValidationStatus, getRoomState } from "@common/lib/utils";
import { computed } from "vue";
import SensorStateRow from "./SensorStateRow.vue";

const props = defineProps<{ area: ShipArea }>();
const roomsWithState = computed<RoomWithState[]>(() =>
  props.area.rooms
    .map((room) => ({ state: getRoomState(room), room }))
    .toSorted((a, b) => compareByValidationStatus(a.state.overall, b.state.overall))
    .toReversed(),
);
</script>

<template>
  <section>
    <header class="flex items-center pb-2 font-bold tracking-wider uppercase md:pb-4 md:text-lg">
      {{ area.name }}

      <span class="grow" />
      <slot
        name="header"
        v-bind="{ area }"
      />
    </header>
    <Table class="bg-background rounded-md py-4">
      <TableBody>
        <SensorStateRow
          v-for="{ room, state } in roomsWithState"
          :key="room.id"
          :room="room"
          :state="state"
        />
      </TableBody>
    </Table>
  </section>
</template>
