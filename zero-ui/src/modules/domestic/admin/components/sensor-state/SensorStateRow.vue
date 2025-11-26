<script setup lang="ts">
import { TableCell, TableRow } from "@/components/ui/table";
import { Room, RoomState } from "@/modules/domestic/types";
import {
  extractActualCO2,
  extractActualHumidity,
  extractActualTemperature,
  formatInt,
} from "@common/lib/utils";
import { DropletsIcon, Fan, ThermometerIcon } from "lucide-vue-next";
import { computed } from "vue";
import SensorStateValue from "./StatusIcon.vue";

const props = defineProps<{ room: Room; state: RoomState }>();

const actualTemperature = computed(() => extractActualTemperature(props.room) ?? 0);
const actualHumidity = computed(() => extractActualHumidity(props.room) ?? 0);
const actualCO2 = computed(() => extractActualCO2(props.room) ?? 0);
</script>

<template>
  <TableRow class="group text-rbase">
    <TableCell class="px-0">{{ room.name }}</TableCell>
    <TableCell class="w-12 px-0">
      <SensorStateValue
        :state="state.temperature"
        :icon="ThermometerIcon"
        class="group-hover:hidden"
      />
      <div class="hidden group-hover:block">
        <span>{{ actualTemperature.toFixed(0) }}</span>
        <sup class="text-rxs top-[-0.3em] font-extralight">&deg;</sup>
      </div>
    </TableCell>
    <TableCell class="w-12 px-0">
      <SensorStateValue
        :state="state.humidity"
        :icon="DropletsIcon"
        class="group-hover:hidden"
      />
      <div class="hidden group-hover:block">
        <span>{{ actualHumidity.toFixed(0) }}</span>
        <span class="text-r2xs ml-[0.25em] font-extralight">&percnt;</span>
      </div>
    </TableCell>
    <TableCell class="w-12 px-0">
      <SensorStateValue
        :state="state.co2"
        class="group-hover:hidden"
        :icon="Fan"
      />
      <div class="hidden group-hover:block">
        <span>{{ formatInt(actualCO2) }}</span>
      </div>
    </TableCell>
  </TableRow>
</template>
