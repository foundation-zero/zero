<script setup lang="ts">
import { DcConverterPairFields, DcConverterPairMimic } from "../dc-converter-pair";

// DC/DC group 2: Brightloops FWD 2 and 1.
const FIELDS: DcConverterPairFields = {
  converters: ["dc:fwd-2", "dc:fwd-1"],
  circuit: "dc:fwd",
  switchValves: ["1068-05", "1068-06"],
  manualValves: ["1167-05", "1167-06"],
  temperatureSensors: ["1038-12", "1038-13"],
  flowSensors: ["1057-11", "1057-12"],
};
</script>

<template>
  <DcConverterPairMimic :fields="FIELDS" />
</template>
