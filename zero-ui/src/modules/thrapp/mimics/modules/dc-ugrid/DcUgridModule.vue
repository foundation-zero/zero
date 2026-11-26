<script setup lang="ts">
import { DcConverterPairFields, DcConverterPairMimic } from "../dc-converter-pair";

// DC/AC group 1: U-Grids 2 and 1.
const FIELDS: DcConverterPairFields = {
  converters: ["dc:ugrid-2", "dc:ugrid-1"],
  circuit: "dc:ugrid",
  switchValves: ["1069-02", "1069-03"],
  manualValves: ["1168-10", "1168-11"],
  temperatureSensors: ["1038-09", "1038-10"],
  flowSensors: ["1057-08", "1057-09"],
};
</script>

<template>
  <DcConverterPairMimic :fields="FIELDS" />
</template>
