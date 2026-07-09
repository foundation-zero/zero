<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils";
import { provideHideEditorIfNotEditable } from "@/modules/thrapp/mimics/providers/forms.ts";
import * as Parameters from "..";
import DHWBoostingHeatpump from "./DHWBoostingHeatpump.vue";
import DHWBoostingHighTemperature from "./DHWBoostingHighTemperature.vue";
import DHWBoostingModeSelection from "./DHWBoostingModeSelection.vue";
import DHWFillingParameters from "./DHWFillingParameters.vue";
import DHWTankSelection from "./DHWTankSelection.vue";

const t = tScoped("thrapp.parameters");

provideHideEditorIfNotEditable(false);
</script>

<template>
  <Parameters.Root>
    <Parameters.Header>
      {{ t("dhw.title") }}
      <Parameters.ResetButton />
    </Parameters.Header>
    <DHWTankSelection />
    <DHWFillingParameters />
    <DHWBoostingModeSelection />
    <DHWBoostingHeatpump />
    <DHWBoostingHighTemperature />
  </Parameters.Root>
</template>
