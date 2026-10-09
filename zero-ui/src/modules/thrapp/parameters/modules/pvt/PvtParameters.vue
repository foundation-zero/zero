<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils";
import { provideHideEditorIfNotEditable } from "@/modules/thrapp/mimics/providers/forms.ts";
import * as Parameters from "../../components/module-parameters/index.ts";
import PvtPidTuning from "./sections/PvtPidTuning.vue";
import PvtPumpControl from "./sections/PvtPumpControl.vue";
import PvtTemperatureSettings from "./sections/PvtTemperatureSettings.vue";

const t = tScoped("thrapp.parameters");

provideHideEditorIfNotEditable(false);
</script>

<template>
  <Parameters.Root>
    <Parameters.Header>
      {{ t("pvt.title") }}
      <Parameters.ResetButton />
    </Parameters.Header>
    <PvtTemperatureSettings />
    <PvtPumpControl />
  </Parameters.Root>

  <Parameters.Pid class="mt-6">
    <Parameters.Header>
      {{ t("pid.title") }}
    </Parameters.Header>
    <PvtPidTuning />
  </Parameters.Pid>
</template>
