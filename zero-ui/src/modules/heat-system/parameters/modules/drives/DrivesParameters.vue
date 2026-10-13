<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils";
import { provideHideEditorIfNotEditable } from "@/modules/heat-system/mimics/providers/forms.ts";
import * as Parameters from "../../components/module-parameters/index.ts";
import DrivesFlowSettings from "./sections/DrivesFlowSettings.vue";
import DrivesPidTuning from "./sections/DrivesPidTuning.vue";
import DrivesTemperatureSettings from "./sections/DrivesTemperatureSettings.vue";

const t = tScoped("heatSystem.parameters");

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

  <Parameters.Pid class="mt-6">
    <Parameters.Header>
      {{ t("pid.title") }}
    </Parameters.Header>
    <DrivesPidTuning />
  </Parameters.Pid>
</template>
