<script setup lang="ts">
import { ExtractSensorFields } from "@/modules/thrapp/types/fields.ts";
import { MimicComponentType } from "@/modules/thrapp/types/index.ts";
import { useTranslations } from "..";
import { SensorValue } from "../../providers";

import * as Partials from "./";
const { items } = useTranslations();

defineProps<ExtractSensorFields<MimicComponentType.BoilerTank>>();
</script>

<template>
  <SensorValue :source="sensors.boostReturnValve">
    <Partials.ListItem size="sm">
      {{ items("boostReturnValve") }}
    </Partials.ListItem>
  </SensorValue>

  <SensorValue :source="sensors.boostSupplyValve">
    <Partials.ListItem size="sm">
      {{ items("boostSupplyValve") }}
    </Partials.ListItem>
  </SensorValue>

  <SensorValue :source="sensors.supplyValve">
    <Partials.ListItem size="sm">
      {{ items("supplyValve") }}
    </Partials.ListItem>
  </SensorValue>

  <SensorValue :source="sensors.dischargeValve">
    <Partials.ListItem size="sm">
      {{ items("dischargeValve") }}
    </Partials.ListItem>
  </SensorValue>
</template>
