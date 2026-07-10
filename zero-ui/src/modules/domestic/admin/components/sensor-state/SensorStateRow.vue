<script setup lang="ts">
import { TableCell, TableRow } from "@/components/ui/table";
import { Room, RoomState } from "@/modules/domestic/types";
import {
  extractActualCO2,
  extractActualHumidity,
  extractActualTemperature,
  formatInt,
} from "@common/lib/utils";
import { RiDropLine, RiThermometerLine, RiWindyLine } from "@remixicon/vue";
import { computed } from "vue";
import SensorStateValue from "./StatusIcon.vue";

const props = defineProps<{ room: Room; state: RoomState }>();

const actualTemperature = computed(() => extractActualTemperature(props.room) ?? 0);
const actualHumidity = computed(() => extractActualHumidity(props.room) ?? 0);
const actualCO2 = computed(() => extractActualCO2(props.room) ?? 0);
</script>

<template>
  <TableRow class="group">
    <TableCell class="">
      <RouterLink
        :to="{
          name: 'cabin:air-conditioning',
          query: { room: room.id, returnUrl: 'environment:control' },
        }"
        class="w-full font-medium hover:underline"
      >
        {{ room.name }}
      </RouterLink>
    </TableCell>
    <TableCell class="w-12 md:w-16">
      <SensorStateValue
        :state="state.temperature"
        :icon="RiThermometerLine"
        class="group-hover:hidden"
      />
      <div class="hidden group-hover:block">
        <span>{{ actualTemperature.toFixed(0) }}</span>
        <sup class="top-[-0.3em] text-xs font-extralight">&deg;</sup>
      </div>
    </TableCell>
    <TableCell class="w-12 md:w-16">
      <SensorStateValue
        :state="state.humidity"
        :icon="RiDropLine"
        class="group-hover:hidden"
      />
      <div class="hidden group-hover:block">
        <span>{{ actualHumidity.toFixed(0) }}</span>
        <span class="ml-[0.25em] text-xs font-extralight">&percnt;</span>
      </div>
    </TableCell>
    <TableCell class="w-12 md:w-16">
      <SensorStateValue
        :state="state.co2"
        class="group-hover:hidden"
        :icon="RiWindyLine"
      />
      <div class="hidden group-hover:block">
        <span>{{ formatInt(actualCO2) }}</span>
      </div>
    </TableCell>
  </TableRow>
</template>
