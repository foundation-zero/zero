<script setup lang="ts">
import { Room, RoomState } from "@/@types";
import { formatInt } from "@/lib/utils";
import { TableCell, TableRow } from "@components/shadcn/table";
import { DropletsIcon, Fan, ThermometerIcon } from "lucide-vue-next";
import SensorStateValue from "./StatusIcon.vue";

defineProps<{ room: Room; state: RoomState }>();
</script>

<template>
  <TableRow class="group text-rbase">
    <TableCell class="px-0 font-medium">{{ room.name }}</TableCell>
    <TableCell class="w-12 px-0">
      <SensorStateValue
        :state="state.temperature"
        :icon="ThermometerIcon"
        class="group-hover:hidden"
      />
      <div class="hidden group-hover:block">
        <span>{{ room.actualTemperature.toFixed(0) }}</span>
        <sup class="top-[-0.3em] text-rxs font-extralight">&deg;</sup>
      </div>
    </TableCell>
    <TableCell class="w-12 px-0">
      <SensorStateValue
        :state="state.humidity"
        :icon="DropletsIcon"
        class="group-hover:hidden"
      />
      <div class="hidden group-hover:block">
        <span>{{ room.actualHumidity.toFixed(0) }}</span>
        <span class="ml-[0.25em] text-r2xs font-extralight">&percnt;</span>
      </div>
    </TableCell>
    <TableCell class="w-12 px-0">
      <SensorStateValue
        :state="state.co2"
        class="group-hover:hidden"
        :icon="Fan"
      />
      <div class="hidden group-hover:block">
        <span>{{ formatInt(room.actualCO2) }}</span>
      </div>
    </TableCell>
  </TableRow>
</template>
