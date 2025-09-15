<script setup lang="ts">
import { RoomWithState, ShipArea } from "@/@types";
import { Table, TableBody } from "@/components/ui/shadcn/table";
import { compareByValidationStatus, getRoomState } from "@/lib/utils";
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
  <section
    class="text-[0.8rem] md:text-[0.9rem] lg:text-[0.95rem] xl:text-[1.2rem] portrait:lg:text-[1rem]"
  >
    <header
      class="text-rxl text-muted-foreground flex items-center pb-2 font-bold tracking-wider uppercase md:pb-4"
    >
      {{ area.name }}

      <span class="grow" />
      <slot
        name="header"
        v-bind="{ area }"
      />
    </header>
    <Table>
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
