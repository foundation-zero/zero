<script setup lang="ts">
import { SensorComponentType } from "@/modules/thrsim/types";
import * as Partials from ".";
import { useTranslations } from "..";
import { ModuleField, SensorValue } from "../../providers";
const { items } = useTranslations();

defineProps<{ valve: ModuleField<SensorComponentType.Valve> }>();
</script>

<template>
  <SensorValue
    :source="valve"
    field="positionRel"
  >
    <Partials.ListItem no-source>
      {{ items("relativePosition") }}
    </Partials.ListItem>
  </SensorValue>
  <SensorValue
    :source="valve"
    field="positionAbs"
  >
    <Partials.ListItem no-source>
      {{ items("absolutePosition") }}
    </Partials.ListItem>
  </SensorValue>
</template>
