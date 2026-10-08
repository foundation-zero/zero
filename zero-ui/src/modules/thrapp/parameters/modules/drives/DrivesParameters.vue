<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils";
import { provideHideEditorIfNotEditable } from "@/modules/thrapp/mimics/providers/forms.ts";
import * as Parameters from "../../components/module-parameters/index.ts";
import DrivesFlowSettings from "./sections/DrivesFlowSettings.vue";
import DrivesTemperatureSettings from "./sections/DrivesTemperatureSettings.vue";

const t = tScoped("thrapp.parameters");

provideHideEditorIfNotEditable(false);
</script>

<template>
  <Parameters.Root>
    <Parameters.Header>
      {{ t("drives.title") }}
      <Parameters.ResetButton />
    </Parameters.Header>
    <DrivesTemperatureSettings />
    <DrivesFlowSettings />
  </Parameters.Root>
</template>
